from flask import Flask, request
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes
import os
import json
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
STATE_FILE = "state.txt"

# Flask app
app_flask = Flask(__name__)

# Inizializza Telegram application
telegram_app = Application.builder().token(TOKEN).build()


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


# Comandi e callback
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
    modified = False

    if query.data == "increase":
        state["button1_presses"] += 1
        if state["button1_presses"] >= 2:
            state["count"] += 1
            state["button1_presses"] = 0
            modified = True
    elif query.data == "decrease":
        state["count"] -= 1
        # state["button1_presses"] = 0
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


# Gestione webhook da Flask
@app_flask.route("/webhook", methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(force=True), telegram_app.bot)
    await telegram_app.process_update(update)
    return "OK"


# Avvia il bot e imposta il webhook
if __name__ == '__main__':
    telegram_app.add_handler(CommandHandler("start", start))
    telegram_app.add_handler(CallbackQueryHandler(button_handler))

    # Imposta webhook
    import asyncio
    async def set_webhook():
        await telegram_app.bot.set_webhook(url=f"{WEBHOOK_URL}")

    asyncio.run(set_webhook())

    print("Avvio Flask...")
    app_flask.run(host="0.0.0.0", port=5000)
