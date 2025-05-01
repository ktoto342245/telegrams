from telegram import Update, ChatPermissions
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from datetime import datetime, timedelta
import time

# Токен бота
TOKEN = "7752116262:AAHW5JE9WCMftH8oH4rTUGmVaS35Dta72lM"  # 🔴 Замініть на свій токен

# Список для виклику
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

# Таймер для "калл"
last_call_time = {}
CALL_TIMEOUT = 180  # сек

# Обробник звичайних повідомлень
def message_handler(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    now = time.time()
    text = update.message.text.strip().lower()

    if text.startswith("калл"):
        last_time = last_call_time.get(chat_id, 0)
        if now - last_time < CALL_TIMEOUT:
            remaining = int(CALL_TIMEOUT - (now - last_time))
            update.message.reply_text(f"⏳ Зачекайте {remaining} сек. перед наступним викликом.")
            return

        last_call_time[chat_id] = now

        extra_text = update.message.text[4:].strip()
        message = f"📣 Призов учасників:\n{USER_LIST}"
        if extra_text:
            message += f"\n\n💬 Повідомлення: {extra_text}"
        update.message.reply_text(message)

# Команда /mut — мут по reply
def mute_handler(update: Update, context: CallbackContext):
    if not update.message.reply_to_message:
        update.message.reply_text("⚠️ Щоб замутити, відповідай на повідомлення користувача.")
        return

    try:
        args = context.args
        if len(args) < 2:
            update.message.reply_text("⚠️ Формат: /mut <хвилин> <причина>")
            return

        duration = int(args[0])
        reason = ' '.join(args[1:])
        user_to_mute = update.message.reply_to_message.from_user

        until_date = datetime.utcnow() + timedelta(minutes=duration)
        permissions = ChatPermissions(can_send_messages=False)

        context.bot.restrict_chat_member(
            chat_id=update.effective_chat.id,
            user_id=user_to_mute.id,
            permissions=permissions,
            until_date=until_date
        )

        update.message.reply_text(
            f"🔇 Користувача @{user_to_mute.username or user_to_mute.first_name} замучено на {duration} хв.\nПричина: {reason}"
        )
    except Exception as e:
        update.message.reply_text(f"❌ Помилка при муті: {e}")

# Головна функція
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, message_handler))
    dp.add_handler(CommandHandler("mut", mute_handler))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
