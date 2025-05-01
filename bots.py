from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram.ext import CallbackContext
from telethon import TelegramClient
import logging

# Введіть свої дані
TOKEN = "7752116262:AAHW5JE9WCMftH8oH4rTUGmVaS35Dta72lM"  # Токен бота від @BotFather
API_ID = 13520503  # Ваш API ID від my.telegram.org
API_HASH = "f7db29069679dcccf7244bc67ac0730d"  # Ваш API Hash від my.telegram.org
PHONE = "+380661719550"  # Ваш номер телефону

# Налаштування логування
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Ініціалізація клієнта для Telethon
client = TelegramClient('session_name', API_ID, API_HASH)

# Функція для обробки команди /start
def start(update: Update, context: CallbackContext):
    if update.message.chat.type == 'private':
        update.message.reply_text("Привіт! Я бот, який працює в групах. Напиши слово 'калл' в будь-якій групі, і я упомяну всіх учасників!")
    else:
        update.message.reply_text("Ця команда працює тільки в особистих повідомленнях!")

# Функція для обробки тексту "калл"
async def handle_call(update: Update, context: CallbackContext):
    logger.info(f"Отримано повідомлення в чаті {update.message.chat_id}")
    if update.message.chat.type not in ['group', 'supergroup']:
        update.message.reply_text("Цей бот працює тільки в групах!")
        return

    try:
        # Відкриваємо сесію Telethon
        await client.start(phone=PHONE)
        
        # Отримуємо всіх учасників групи
        members = await client.get_participants(update.message.chat.id)

        mentions = []
        for member in members:
            if not member.bot:
                mentions.append(f"@{member.username}" if member.username else f"[{member.first_name}](tg://user?id={member.id})")

        if mentions:
            response = "Призив почато: \n" + " ".join(mentions)
        else:
            response = "Учасники не знайдені."

        update.message.reply_text(response, parse_mode="Markdown")

    except Exception as e:
        logger.error(f"Помилка при отриманні списку учасників: {e}")
        update.message.reply_text(f"Сталася помилка: {str(e)}")

# Функція для обробки текстових повідомлень
def text_handler(update: Update, context: CallbackContext):
    message_text = update.message.text.lower().strip()
    logger.info(f"Отримано текст: {message_text}")
    if "калл" in message_text:  # Перевіряємо наявність слова "калл"
        context.job_queue.run_once(lambda context: handle_call(update, context), 0)

# Функція для обробки помилок
def error_handler(update: Update, context: CallbackContext):
    logger.error(f"Update {update} caused error {context.error}")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, text_handler))
    dp.add_error_handler(error_handler)

    updater.start_polling()
    logger.info("Бот запущено")
    updater.idle()

if __name__ == '__main__':
    main()
