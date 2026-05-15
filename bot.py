import json
import os

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = "ТВОЙ_ТОКЕН"

DATA_FILE = "bank.json"

current_user = {}

users = {
    "Кот": {
        "positive": "Доволен",
        "negative": "Не доволен"
    },
    "Киса": {
        "positive": "Довольна",
        "negative": "Не довольна"
    }
}


def load_data():
    if not os.path.exists(DATA_FILE):
        return {
            "Кот": 0,
            "Киса": 0
        }

    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def get_total_bank(data):
    return data["Кот"] + data["Киса"]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = ReplyKeyboardMarkup(
        [
            ["Кот", "Киса"]
        ],
        resize_keyboard=True
    )

    await update.message.reply_text(
        "Выбери пользователя:",
        reply_markup=keyboard
    )


async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    text = update.message.text

    data = load_data()

    if text == "Кот" or text == "Киса":
        current_user[chat_id] = text

        keyboard = ReplyKeyboardMarkup(
            [
                [users[text]["positive"], users[text]["negative"]],
                ["Назад"]
            ],
            resize_keyboard=True
        )

        await update.message.reply_text(
            f"Выбран пользователь: {text}",
            reply_markup=keyboard
        )
        return

    if text == "Назад":
        await start(update, context)
        return

    if chat_id not in current_user:
        await start(update, context)
        return

    selected_user = current_user[chat_id]

    positive_button = users[selected_user]["positive"]
    negative_button = users[selected_user]["negative"]

    if text == positive_button:
        data[selected_user] += 300
        save_data(data)

        await update.message.reply_text(
            f"+300 рублей.\n"
            f"Сейчас у {selected_user} в копилке: {data[selected_user]} рублей.\n"
            f"Общее количество средств в банке: {get_total_bank(data)} рублей."
        )

    elif text == negative_button:
        data[selected_user] -= 300
        save_data(data)

        await update.message.reply_text(
            f"-300 рублей.\n"
            f"Сейчас у {selected_user} в копилке: {data[selected_user]} рублей.\n"
            f"Общее количество средств в банке: {get_total_bank(data)} рублей."
        )

    else:
        await update.message.reply_text("Выбери кнопку ниже.")


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT, text_handler))

app.run_polling()