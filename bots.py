from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import Update
import logging
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Токен вашего бота из переменной окружения
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or "7752116262:AAHW5JE9WCMftH8oH4rTUGmVaS35Dta72lM"

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Функция для обработки команды /start в ЛС
def start(update: Update, context):
    if update.message.chat.type == 'private':
        update.message.reply_text("Привет! Я бот, который работает в группах. Напиши 'калл' в любой группе, и я покажу список администраторов!")
    else:
        update.message.reply_text("Эта команда работает только в личных сообщениях!")

# Функция для обработки команды или текста "калл"
def handle_call(update: Update, context):
    logger.info(f"Получено сообщение 'калл' в чате {update.message.chat_id}")
    if update.message.chat.type not in ['group', 'supergroup']:
        update.message.reply_text("Этот бот работает только в группах!")
        return

    try:
        members = []
        admins = context.bot.get_chat_administrators(update.message.chat_id)
        logger.info(f"Найдено администраторов: {len(admins)}")
        admin_ids = {admin.user.id for admin in admins}

        for admin in admins:
            username = admin.user.username or admin.user.first_name
            members.append(f"@{username}" if admin.user.username else username)

        if members:
            response = "Администраторы группы:\n" + "\n".join(members)
        else:
            response = "Администраторы не найдены."

        update.message.reply_text(response)

    except Exception as e:
        logger.error(f"Ошибка при получении списка участников: {e}")
        update.message.reply_text("Произошла ошибка при получении списка участников.")

# Функция для обработки текстовых сообщений
def text_handler(update: Update, context):
    message_text = update.message.text.lower().strip()
    logger.info(f"Получен текст: {message_text}")
    if message_text.startswith("калл"):
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
