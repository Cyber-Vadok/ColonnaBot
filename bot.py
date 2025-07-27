import os
import json
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
STATE_FILE = "state.txt"

# Stato locale
def load_state():
    if not os.path.exists(STATE_FILE):
        state = {"count": 0, "button1_presses": 0}
        save_state(state)
    else:
        with open(STATE_FILE, "r") as f:
            state = json.load(f)
    return state

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔼 Aumenta", callback_data="increase")],
        [InlineKeyboardButton("🔽 Diminuisci", callback_data="decrease")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    state = load_state()
    await update.message.reply_text(
        f"Contatore: {state['count']}", reply_markup=reply_markup
    )

# Gestione dei bottoni
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    state_before = load_state()
    state = state_before.copy()
    modified = False

    if query.data == "increase":
        state["button1_presses"] += 1
        if state["button1_presses"] >= 2:
            state["count"] += 1
            state["button1_presses"] = 0
            modified = True
    elif query.data == "decrease":
        state["count"] -= 1
        modified = True

    save_state(state)

    if modified:
        keyboard = [
            [InlineKeyboardButton("🔼 Aumenta", callback_data="increase")],
            [InlineKeyboardButton("🔽 Diminuisci", callback_data="decrease")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text=f"Contatore: {state['count']}",
            reply_markup=reply_markup
        )

# Main
if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("Bot avviato. Premi CTRL+C per uscire.")
    app.run_polling()
