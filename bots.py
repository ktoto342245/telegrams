from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import Update
from telethon.sync import TelegramClient
import logging
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Переменные окружения
TOKEN = os.getenv("7752116262:AAHW5JE9WCMftH8oH4rTUGmVaS35Dta72lM")
API_ID = os.getenv("13520503")
API_HASH = os.getenv("f7db29069679dcccf7244bc67ac0730d")
PHONE = os.getenv("+380661719550")

# Проверка наличия всех переменных
if not all([TOKEN, API_ID, API_HASH, PHONE]):
    missing = [var for var, val in [("TOKEN", TOKEN), ("API_ID", API_ID), ("API_HASH", API_HASH), ("PHONE", PHONE)] if not val]
    raise ValueError(f"Missing environment variables: {', '.join(missing)}")

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Функция для обработки команды /start в ЛС
def start(update: Update, context):
    if update.message.chat.type == 'private':
        update.message.reply_text("Привет! Я бот, который работает в группах. Напиши слово 'калл' в любой группе, и я упомяну всех участников!")
    else:
        update.message.reply_text("Эта команда работает только в личных сообщениях!")

# Функция для обработки команды или текста "калл"
def handle_call(update: Update, context):
    logger.info(f"Получено сообщение в чате {update.message.chat_id}")
    if update.message.chat.type not in ['group', 'supergroup']:
        update.message.reply_text("Этот бот работает только в группах!")
        return

    try:
        # Инициализация Telethon клиента
        client = TelegramClient('session', int(API_ID), API_HASH)
        with client:
            # Получаем всех участников группы
            members = []
            for member in client.get_participants(update.message.chat_id):
                username = member.username or member.first_name
                if member.username:  # Упоминаем только тех, у кого есть username
                    members.append(f"@{username}")
                else:
                    members.append(username)

            if members:
                response = "начинаю призыв:\n" + "\n".join(members)
            else:
                response = "Участники не найдены."

            update.message.reply_text(response)

    except Exception as e:
        logger.error(f"Ошибка при получении списка участников: {e}")
        update.message.reply_text(f"Произошла ошибка: {str(e)}")

# Функция для обработки текстовых сообщений
def text_handler(update: Update, context):
    message_text = update.message.text.lower().strip()
    logger.info(f"Получен текст: {message_text}")
    if "калл" in message_text:  # Проверяем наличие слова "калл"
        handle_call(update, context)

# Функция для обработки ошибок
def error_handler(update: Update, context):
    logger.error(f"Update {update} caused error {context.error}")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, text_handler))
    dp.add_error_handler(error_handler)

    updater.start_polling()
    logger.info("Бот запущен")
    updater.idle()

if __name__ == '__main__':
    main()
