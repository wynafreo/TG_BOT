import os
import json
import requests
from flask import Flask, request

TOKEN = os.environ["BOT_TOKEN"]
WEBHOOK_SECRET = os.environ["WEBHOOK_SECRET"]

DATA_FILE = "bank.json"

app = Flask(__name__)

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

current_user = {}


def load_data():
    if not os.path.exists(DATA_FILE):
        return {"Кот": 0, "Киса": 0}

    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def send_message(chat_id, text, keyboard=None):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": text
    }

    if keyboard:
        payload["reply_markup"] = {
            "keyboard": keyboard,
            "resize_keyboard": True
        }

    requests.post(url, json=payload)


def show_users(chat_id):
    send_message(
        chat_id,
        "Выбери пользователя:",
        [["Кот", "Киса"]]
    )


@app.route("/")
def index():
    return "Bot is running"


@app.route(f"/webhook/{WEBHOOK_SECRET}", methods=["POST"])
def webhook():
    update = request.get_json()

    if "message" not in update:
        return "ok"

    message = update["message"]
    chat_id = message["chat"]["id"]
    text = message.get("text", "")

    data = load_data()

    if text == "/start":
        show_users(chat_id)
        return "ok"

    if text in ["Кот", "Киса"]:
        current_user[str(chat_id)] = text

        send_message(
            chat_id,
            f"Выбран пользователь: {text}",
            [[users[text]["positive"], users[text]["negative"]], ["Назад"]]
        )
        return "ok"

    if text == "Назад":
        show_users(chat_id)
        return "ok"

    chat_key = str(chat_id)

    if chat_key not in current_user:
        show_users(chat_id)
        return "ok"

    selected_user = current_user[chat_key]

    if text == users[selected_user]["positive"]:
        data[selected_user] += 300
        save_data(data)

        total = data["Кот"] + data["Киса"]

        send_message(
            chat_id,
            f"+300 рублей.\n"
            f"Сейчас у {selected_user} в копилке: {data[selected_user]} рублей.\n"
            f"Общее количество средств в банке: {total} рублей."
        )
        return "ok"

    if text == users[selected_user]["negative"]:
        data[selected_user] -= 300
        save_data(data)

        total = data["Кот"] + data["Киса"]

        send_message(
            chat_id,
            f"-300 рублей.\n"
            f"Сейчас у {selected_user} в копилке: {data[selected_user]} рублей.\n"
            f"Общее количество средств в банке: {total} рублей."
        )
        return "ok"

    send_message(chat_id, "Выбери кнопку ниже.")
    return "ok"