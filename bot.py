from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes
import os
import json
from dotenv import load_dotenv

STATE_FILE = "state.txt"

# Inizializza lo stato se non esiste
def load_state():
    if not os.path.exists(STATE_FILE):
        state = {
            "count": 0,
            "button1_presses": 0
        }
        save_state(state)
    else:
        with open(STATE_FILE, "r") as f:
            state = json.load(f)
    return state

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

# Mostra i pulsanti
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

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    state_before = load_state()
    state = state_before.copy()
    modified = False  # flag per verificare se il messaggio deve essere aggiornato

    if query.data == "increase":
        state["button1_presses"] += 1
        if state["button1_presses"] >= 2:
            state["count"] += 1
            state["button1_presses"] = 0
            modified = True
    elif query.data == "decrease":
        state["count"] -= 1
        state["button1_presses"] = 0
        modified = True

    save_state(state)

    # aggiorna solo se è cambiato qualcosa
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
if __name__ == '__main__':
    import os
    # Carica il file .env
    load_dotenv()

    # Ottieni il token
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot in esecuzione...")
    app.run_polling()
