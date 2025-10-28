import requests
from time import sleep
from mistralai import Mistral
from langdetect import detect

# ==== 🔑 Вставь свои ключи ====
TELEGRAM_BOT_TOKEN = "8383958081:AAHCdEr-K_TuO7JKXjE8bEr-FvoemWZOKQ4"
MISTRAL_API_KEY = "57EalUtv5CCfN7FJSm0IkFG0Ki5xaJXi"

# ==== Настройки ====
mistral = Mistral(api_key=MISTRAL_API_KEY)
URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
offset = 0

print("🤖 Бот запущен. Напиши ему в Telegram!")

# Словарь для хранения последних 5 сообщений каждого пользователя
user_history = {}

def get_updates():
    global offset
    response = requests.get(URL + "/getUpdates", params={"offset": offset, "timeout": 30})
    data = response.json()
    return data.get("result", [])

def send_message(chat_id, text):
    requests.post(URL + "/sendMessage", data={"chat_id": chat_id, "text": text})

while True:
    updates = get_updates()
    for update in updates:
        offset = update["update_id"] + 1

        if "message" in update and "text" in update["message"]:
            chat_id = update["message"]["chat"]["id"]
            user_text = update["message"]["text"].strip()

            # Фиксируем язык на русский
            lang = "ru"

            # Инициализация истории для пользователя
            if chat_id not in user_history:
                user_history[chat_id] = []

            # Добавляем текущее сообщение в историю
            user_history[chat_id].append(f"Пользователь: {user_text}")
            if len(user_history[chat_id]) > 5:
                user_history[chat_id] = user_history[chat_id][-5:]

            # Prompt для Мistral
            system_prompt = (
                f"Ты — добрый, эмпатичный психолог. "
                f"Отвечай на русском языке. "
                f"Используй психологические техники, чтобы пользователю было комфортно: "
                f"подтверждай чувства, задавай мягкие вопросы, давай лёгкие позитивные советы. "
                f"Сохраняй ответы короткими, тёплыми и естественными.\n\n"
                f"История беседы:\n" + "\n".join(user_history[chat_id])
            )

            try:
                response = mistral.chat.complete(
                    model="mistral-large-latest",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_text}
                    ]
                )

                reply = response.choices[0].message.content.strip()
                send_message(chat_id, reply)

                # Добавляем ответ ИИ в историю
                user_history[chat_id].append(f"Бот: {reply}")
                if len(user_history[chat_id]) > 5:
                    user_history[chat_id] = user_history[chat_id][-5:]

            except Exception as e:
                print("⚠️ Ошибка:", e)
                send_message(chat_id, "Произошла ошибка при подключении к ИИ. Проверь API ключ.")

    sleep(2)
