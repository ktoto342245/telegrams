from telegram import Update, ChatPermissions
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from datetime import datetime, timedelta
import time
import re

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

# Функція для конвертації тривалості у секунди
def parse_duration(duration_str):
    total_seconds = 0
    # Регулярні вирази для кожної одиниці часу
    pattern = r'(\d+)([smhdMy])'  # Пошук чисел з одиницями часу
    
    matches = re.findall(pattern, duration_str)
    
    for value, unit in matches:
        value = int(value)
        if unit == 'сек':  # Секунди
            total_seconds += value
        elif unit == 'мин':  # Хвилини
            total_seconds += value * 60
        elif unit == 'час':  # Години
            total_seconds += value * 3600
        elif unit == 'дни':  # Дні
            total_seconds += value * 86400
        elif unit == 'месяц':  # Місяці
            total_seconds += value * 2592000  # 30 днів на місяць
        elif unit == 'Год':  # Роки
            total_seconds += value * 31536000  # 365 днів на рік
    
    return total_seconds

# Обробник звичайних повідомлень
def message_handler(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    now = time.time()
    text = update.message.text.strip().lower()

    if text.startswith("калл"):
        last_time = last_call_time.get(chat_id, 0)
        if now - last_time < CALL_TIMEOUT:
            remaining = int(CALL_TIMEOUT - (now - last_time))
            update.message.reply_text(f"⏳ Подождите {remaining} сек. перед следуйщим вызовом.")
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
        update.message.reply_text("⚠️ Чтобы замутить, отвечатьте на сообщения пользователя.")
        return

    try:
        args = context.args
        if len(args) < 2:
            update.message.reply_text("⚠️ Формат: /mut <хв> <причина>")
            return

        # Парсимо тривалість за допомогою функції
        duration_str = args[0]
        duration_seconds = parse_duration(duration_str)
        
        if duration_seconds == 0:
            update.message.reply_text("⚠️ Невірний формат тривалості.")
            return

        reason = ' '.join(args[1:])
        user_to_mute = update.message.reply_to_message.from_user

        until_date = datetime.utcnow() + timedelta(seconds=duration_seconds)
        permissions = ChatPermissions(can_send_messages=False)

        context.bot.restrict_chat_member(
            chat_id=update.effective_chat.id,
            user_id=user_to_mute.id,
            permissions=permissions,
            until_date=until_date
        )

        update.message.reply_text(
            f"🔇 Користувача @{user_to_mute.username or user_to_mute.first_name} замучено на {duration_str}.\nПричина: {reason}"
        )
    except Exception as e:
        update.message.reply_text(f"❌ Помилка при муті: {e}")

# Команда /unmut — розмутити користувача
def unmute_handler(update: Update, context: CallbackContext):
    if not update.message.reply_to_message:
        update.message.reply_text("⚠️ Чтобы размутить, отвечает на сообщения пользователя.")
        return

    try:
        user_to_unmute = update.message.reply_to_message.from_user
        permissions = ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_polls=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True,
            can_change_info=False,
            can_invite_users=True,
            can_pin_messages=False
        )

        context.bot.restrict_chat_member(
            chat_id=update.effective_chat.id,
            user_id=user_to_unmute.id,
            permissions=permissions
        )

        update.message.reply_text(
            f"🔊 Учасник @{user_to_unmute.username or user_to_unmute.first_name} розмутили."
        )
    except Exception as e:
        update.message.reply_text(f"❌ Ошибка: {e}")

# Головна функція
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, message_handler))
    dp.add_handler(CommandHandler("mut", mute_handler))
    dp.add_handler(CommandHandler("unmut", unmute_handler))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
