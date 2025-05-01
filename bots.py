from telegram import Update, ChatPermissions
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext, CommandHandler
import time
from datetime import timedelta

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

# Таймер останнього виклику (по chat_id)
last_call_time = {}
CALL_TIMEOUT = 180  # в секундах

def message_handler(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    now = time.time()
    text = update.message.text.strip()

    if text.lower().startswith("калл"):
        last_time = last_call_time.get(chat_id, 0)
        if now - last_time < CALL_TIMEOUT:
            remaining = int(CALL_TIMEOUT - (now - last_time))
            update.message.reply_text(f"⏳ Подождите {remaining} сек. перед следующим вызовом.")
            return

        # Обновляем время последнего вызова
        last_call_time[chat_id] = now

        extra_text = text[4:].strip()  # Все, що після "калл"
        message = f"Призыв начат:\n{USER_LIST}"
        if extra_text:
            message += f"\n\n📣 Сообщение от пользователя:\n{extra_text}"
        update.message.reply_text(message)

# Команда /mut
def mute_handler(update: Update, context: CallbackContext):
    try:
        args = update.message.text.split(maxsplit=3)
        if len(args) < 4:
            update.message.reply_text("⚠️ Формат: /mut <хвилин> <причина> @username")
            return

        duration = int(args[1])
        reason = args[2]
        username = args[3].lstrip("@")

        chat = update.effective_chat

        # Отримання користувача по username
        member = chat.get_member(update.message.reply_to_message.from_user.id) if update.message.reply_to_message else None
        if not member:
            for user_id in range(1, 10000):  # умовно
                try:
                    member = chat.get_member(user_id)
                    if member.user.username and member.user.username.lower() == username.lower():
                        break
                except:
                    continue
        if not member:
            update.message.reply_text("❌ Користувача не знайдено.")
            return

        until_date = update.message.date + timedelta(minutes=duration)
        permissions = ChatPermissions(can_send_messages=False)

        context.bot.restrict_chat_member(
            chat_id=chat.id,
            user_id=member.user.id,
            permissions=permissions,
            until_date=until_date
        )

        update.message.reply_text(f"🔇 @{member.user.username} замучений на {duration} хвилин. Причина: {reason}")
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
