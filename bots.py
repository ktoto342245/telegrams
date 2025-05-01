from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging

# Токен бота от @BotFather
TOKEN = "7752116262:AAHW5JE9WCMftH8oH4rTUGmVaS35Dta72lM"

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Функция для обработки команды /start в ЛС
def start(update: Update, context):
    if update.message.chat.type == 'private':
        update.message.reply_text("Привет! Я бот, который работает в группах. Напиши слово 'калл' в любой группе, и я упомяну всех участников!")
    else:
        update.message.reply_text("Эта команда работает только в личных сообщениях!")

# Функция для обработки текста "калл"
def handle_call(update: Update, context):
    logger.info(f"Получено сообщение в чате {update.message.chat_id}")
    if update.message.chat.type not in ['group', 'supergroup']:
        update.message.reply_text("Этот бот работает только в группах!")
        return

    try:
        # Получаем всех участников группы
        chat_id = update.message.chat.id
        members = update.message.chat.get_members()

        mentions = []
        for member in members:
            user = member.user
            if not user.is_bot:
                mentions.append(f"@{user.username}" if user.username else f"[{user.full_name}](tg://user?id={user.id})")

        if mentions:
            response = "Призыв начат: \n" + " ".join(mentions)
        else:
            response = "Участники не найдены."

        update.message.reply_text(response, parse_mode="Markdown")

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
