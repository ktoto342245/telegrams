from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import Update
import logging

# Токен вашего бота от BotFather
TOKEN = "7752116262:AAHW5JE9WCMftH8oH4rTUGmVaS35Dta72lM"

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Функция для обработки команды /start в ЛС
def start(update: Update, context):
    # Проверяем, что сообщение отправлено в личные сообщения
    if update.message.chat.type == 'private':
        update.message.reply_text("Привет! Я бот, который работает в группах. Напиши 'калл' в любой группе, и я покажу список администраторов!")
    else:
        update.message.reply_text("Эта команда работает только в личных сообщениях!")

# Функция для обработки команды или текста "калл"
def handle_call(update: Update, context):
    # Проверяем, что сообщение отправлено в группу или супергруппу
    if update.message.chat.type not in ['group', 'supergroup']:
        update.message.reply_text("Этот бот работает только в группах!")
        return

    # Получаем список участников группы
    try:
        members = []
        # Получаем администраторов группы
        admins = context.bot.get_chat_administrators(update.message.chat_id)
        admin_ids = {admin.user.id for admin in admins}

        for admin in admins:
            username = admin.user.username or admin.user.first_name
            members.append(f"@{username}" if admin.user.username else username)

        # Формируем ответ
        if members:
            response = "Участники группы:\n" + "\n".join(members)
        else:
            response = "Не удалось получить список участников."

        update.message.reply_text(response)

    except Exception as e:
        logger.error(f"Ошибка при получении списка участников: {e}")
        update.message.reply_text("Произошла ошибка при получении списка участников.")

# Функция для обработки текстовых сообщений
def text_handler(update: Update, context):
    message_text = update.message.text.lower().strip()
    # Проверяем, начинается ли сообщение с "калл"
    if message_text.startswith("калл"):
        handle_call(update, context)

# Функция для обработки ошибок
def error_handler(update: Update, context):
    logger.error(f"Update {update} caused error {context.error}")

def main():
    # Создаем Updater и передаем токен
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # Регистрируем обработчик команды /start
    dp.add_handler(CommandHandler("start", start))

    # Регистрируем обработчик текстовых сообщений
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, text_handler))

    # Регистрируем обработчик ошибок
    dp.add_error_handler(error_handler)

    # Запускаем бота
    updater.start_polling()
    logger.info("Бот запущен")
    updater.idle()

if __name__ == '__main__':
    main()
