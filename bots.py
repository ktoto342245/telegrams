from telegram import Update, ChatPermissions
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext, CommandHandler
import datetime
import re

TOKEN = "7752116262:AAHW5JE9WCMftH8oH4rTUGmVaS35Dta72lM"  # 🔁 Заміні на свій токен

USER_LIST = """
@kall_help_bot @Helpmepls53 @zeyka09 @k0ly3 Zxc_top @naznaynepridumal @azaliya_103 
@Virus_na @tromeozey Егор @Klaker_Ghost @Qvistyl @ItaliaAlexSlap @HAURFLOL 
@Potrogaltravu @Zxcpsihuska @COBA_31 @TOR_7_77
"""

# Призыв
def message_handler(update: Update, context: CallbackContext):
    text = update.message.text.lower()
    if "калл" in text:
        user_message = update.message.text
        if user_message.strip().lower() == "калл":
            update.message.reply_text(f"Призыв начат:\n{USER_LIST}")
        else:
            extra_text = user_message.partition("калл")[2].strip()
            update.message.reply_text(f"Призыв начат:\n{USER_LIST}\n\n💬 {extra_text}")

# Команда /mut
def mut_handler(update: Update, context: CallbackContext):
    try:
        args = context.args
        if len(args) < 3:
            update.message.reply_text("❌ Формат: /mut 10m причина @user")
            return

        # Витягуємо дані
        duration_str = args[0]
        reason = ' '.join(args[1:-1])
        username = args[-1]

        # Переводимо тривалість
        match = re.match(r"(\d+)([smhd])", duration_str)
        if not match:
            update.message.reply_text("❌ Невірний формат часу. Приклад: 10m, 1h, 2d")
            return

        amount = int(match.group(1))
        unit = match.group(2)
        if unit == "s":
            delta = datetime.timedelta(seconds=amount)
        elif unit == "m":
            delta = datetime.timedelta(minutes=amount)
        elif unit == "h":
            delta = datetime.timedelta(hours=amount)
        elif unit == "d":
            delta = datetime.timedelta(days=amount)

        until_date = datetime.datetime.utcnow() + delta

        # Пошук користувача
        chat = update.effective_chat
        members = chat.get_members()
        target_user = None
        for member in members:
            if member.user.username and "@" + member.user.username.lower() == username.lower():
                target_user = member.user
                break

        if not target_user:
            update.message.reply_text("❌ Користувач не знайдений у групі.")
            return

        # Видаємо мут
        context.bot.restrict_chat_member(
            chat_id=chat.id,
            user_id=target_user.id,
            permissions=ChatPermissions(can_send_messages=False),
            until_date=until_date
        )

        update.message.reply_text(f"🔇 {username} замучений на {duration_str} з причиною: {reason}")

    except Exception as e:
        update.message.reply_text(f"❌ Помилка: {e}")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, message_handler))
    dp.add_handler(CommandHandler("mut", mut_handler))
    
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
