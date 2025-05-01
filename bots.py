from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext

# Токен бота
TOKEN = "7752116262:AAHW5JE9WCMftH8oH4rTUGmVaS35Dta72lM"  # Замініть на свій токен

# Готовий список користувачів
USER_LIST = """
@kall_help_bot 
@Helpmepls53 
@zeyka09 
@k0ly3 
Zxc_top
@naznaynepridumal 
@azaliya_103 
@Virus_na 
@tromeozey 
Егор 
@Klaker_Ghost 
@Qvistyl 
@ItaliaAlexSlap 
@HAURFLOL 
@Potrogaltravu 
@Zxcpsihuska 
@COBA_31 
@TOR_7_77
"""

# Обробка текстових повідомлень
def message_handler(update: Update, context: CallbackContext):
    text = update.message.text.strip()

    if text.lower().startswith("калл"):
        extra_text = text[4:].strip()  # Все, що після "калл"
        message = f"Призыв начат:\n{USER_LIST}"
        if extra_text:
            message += f"\n\n📣 Сообщение от пользователя:\n{extra_text}"
        update.message.reply_text(message)

# Головна функція
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, message_handler))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
