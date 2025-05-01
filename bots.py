from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext

# Токен бота
TOKEN = "ВАШ_ТОКЕН_ТУТ"  # Заміни на свій токен

# Готовий список користувачів
USER_LIST = """
@kall_help_bot @Helpmepls53 @zeyka09 @k0ly3 Zxc_top @naznaynepridymal @azaliya_103 
@Virus_na @tromeozey Егор @Klaker_Ghost @Qvistyl @ItaliaAlexSlap @HAURFLOL 
@Potrogaltravu @Zxcpsihuska @COBA_31 @TOR_7_77
"""

# Обробка текстових повідомлень
def message_handler(update: Update, context: CallbackContext):
    text = update.message.text.lower()
    if "калл" in text:
        update.message.reply_text(f"Призыв начат:\n{USER_LIST}")

# Головна функція
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, message_handler))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
