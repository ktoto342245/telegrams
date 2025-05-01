from telegram import Update, ChatPermissions, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from datetime import datetime, timedelta
import time
import re
from threading import Timer

TOKEN = "7752116262:AAHW5JE9WCMftH8oH4rTUGmVaS35Dta72lM"
ADMINS = [7896946163, 7137133015, 7618906705]
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
last_call_time = {}
CALL_TIMEOUT = 180
muted_users = {}
# Словник для зберігання ID групи для кожного користувача, який викликав /start
user_group_mapping = {}  # {user_id: group_chat_id}

def parse_duration(duration_str):
    total_seconds = 0
    pattern = r'(\d+)([smhdMy])'
    matches = re.findall(pattern, duration_str)
    
    for value, unit in matches:
        value = int(value)
        if unit == 's':
            total_seconds += value
        elif unit == 'm':
            total_seconds += value * 60
        elif unit == 'h':
            total_seconds += value * 3600
        elif unit == 'd':
            total_seconds += value * 86400
        elif unit == 'M':
            total_seconds += value * 2592000
        elif unit == 'y':
            total_seconds += value * 31536000
    return total_seconds

def format_time_remaining(until_date):
    now = datetime.utcnow()
    delta = until_date - now
    if delta.total_seconds() <= 0:
        return "Мут закончился"
    seconds = int(delta.total_seconds())
    if seconds < 60:
        return f"{seconds} сек."
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes} мин."
    hours = minutes // 60
    if hours < 24:
        return f"{hours} ч."
    days = hours // 24
    return f"{days} дн."

def start_handler(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name
    chat_type = update.effective_chat.type

    if chat_type != "private":
        try:
            # Зберігаємо ID групи для користувача
            user_group_mapping[user_id] = update.effective_chat.id
            
            # Надсилаємо повідомлення в групі
            update.message.reply_text(f"@{username}, я отправил вам команды в личные сообщения!")
            
            # Формуємо клавіатуру для користувача
            is_admin = user_id in ADMINS
            participant_commands = [
                [KeyboardButton("калл"), KeyboardButton("/mutlist")]
            ]
            admin_commands = participant_commands + [
                [KeyboardButton("/mut"), KeyboardButton("/unmut")]
            ]
            keyboard = admin_commands if is_admin else participant_commands
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

            # Надсилаємо клавіатуру в приватний чат користувача
            context.bot.send_message(
                chat_id=user_id,
                text="Выберите команду:",
                reply_markup=reply_markup
            )
        except Exception as e:
            update.message.reply_text(f"⚠️ Не удалось отправить сообщение в личный чат. Пожалуйста, начните диалог со мной, написав /start в личных сообщениях.\nОшибка: {e}")
        return

    # Якщо команда викликана в приватному чаті, показуємо клавіатуру
    is_admin = user_id in ADMINS
    participant_commands = [
        [KeyboardButton("калл"), KeyboardButton("/mutlist")]
    ]
    admin_commands = participant_commands + [
        [KeyboardButton("/mut"), KeyboardButton("/unmut")]
    ]
    keyboard = admin_commands if is_admin else participant_commands
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    update.message.reply_text("Выберите команду:", reply_markup=reply_markup)

def message_handler(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    chat_type = update.effective_chat.type
    chat_id = update.effective_chat.id
    now = time.time()
    text = update.message.text.strip().lower()

    if text.startswith("калл"):
        # Визначаємо, куди надсилати відповідь
        target_chat_id = chat_id
        if chat_type == "private" and user_id in user_group_mapping:
            target_chat_id = user_group_mapping[user_id]

        last_time = last_call_time.get(target_chat_id, 0)
        if now - last_time < CALL_TIMEOUT:
            remaining = int(CALL_TIMEOUT - (now - last_time))
            context.bot.send_message(
                chat_id=target_chat_id,
                text=f"⏳ Подождите {remaining} сек. перед следующим вызовом."
            )
            return

        last_call_time[target_chat_id] = now
        extra_text = update.message.text[4:].strip()
        message = f"📣 Призыв участников:\n{USER_LIST}"
        if extra_text:
            message += f"\n\n💬 Сообщение: {extra_text}"
        context.bot.send_message(
            chat_id=target_chat_id,
            text=message
        )

def mute_handler(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    chat_type = update.effective_chat.type
    chat_id = update.effective_chat.id

    # Визначаємо, куди надсилати відповідь
    target_chat_id = chat_id
    if chat_type == "private" and user_id in user_group_mapping:
        target_chat_id = user_group_mapping[user_id]

    if user_id not in ADMINS:
        context.bot.send_message(
            chat_id=target_chat_id,
            text=" У вас нет прав для использования этой команды."
        )
        return

    if not update.message.reply_to_message:
        context.bot.send_message(
            chat_id=target_chat_id,
            text="⚠️ Чтобы замутить, отвечайте на сообщение пользователя. (формат мутов: 's = сек; m = мин; h = часы; d = дни; M = месяц; y = год')"
        )
        return

    try:
        args = context.args
        if len(args) < 2:
            context.bot.send_message(
                chat_id=target_chat_id,
                text="⚠️ Формат: /mut <время> <причина>"
            )
            return

        duration_str = args[0]
        duration_seconds = parse_duration(duration_str)
        
        if duration_seconds == 0:
            context.bot.send_message(
                chat_id=target_chat_id,
                text="⚠️ Неверный формат длительности."
            )
            return

        reason = ' '.join(args[1:])
        user_to_mute = update.message.reply_to_message.from_user
        until_date = datetime.utcnow() + timedelta(seconds=duration_seconds)
        permissions = ChatPermissions(can_send_messages=False)

        context.bot.restrict_chat_member(
            chat_id=target_chat_id,
            user_id=user_to_mute.id,
            permissions=permissions,
            until_date=until_date
        )

        if target_chat_id not in muted_users:
            muted_users[target_chat_id] = {}
        muted_users[target_chat_id][user_to_mute.id] = {
            'username': user_to_mute.username or user_to_mute.first_name,
            'until_date': until_date,
            'reason': reason
        }

        context.bot.send_message(
            chat_id=target_chat_id,
            text=f"🔇 Пользователь @{user_to_mute.username or user_to_mute.first_name} замучен на {duration_str}.\nПричина: {reason}"
        )

        if duration_seconds <= 30:
            def unmute_later():
                try:
                    context.bot.restrict_chat_member(
                        chat_id=target_chat_id,
                        user_id=user_to_mute.id,
                        permissions=ChatPermissions(
                            can_send_messages=True,
                            can_send_media_messages=True,
                            can_send_polls=True,
                            can_send_other_messages=True,
                            can_add_web_page_previews=True,
                            can_change_info=False,
                            can_invite_users=True,
                            can_pin_messages=False
                        )
                    )
                    if target_chat_id in muted_users and user_to_mute.id in muted_users[target_chat_id]:
                        del muted_users[target_chat_id][user_to_mute.id]
                        if not muted_users[target_chat_id]:
                            del muted_users[target_chat_id]
                except Exception as e:
                    print(f"❌ Ошибка авторазмута: {e}")
            Timer(duration_seconds, unmute_later).start()

    except Exception as e:
        context.bot.send_message(
            chat_id=target_chat_id,
            text=f"❌ Ошибка при муте: {e}"
        )

def unmute_handler(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    chat_type = update.effective_chat.type
    chat_id = update.effective_chat.id

    # Визначаємо, куди надсилати відповідь
    target_chat_id = chat_id
    if chat_type == "private" and user_id in user_group_mapping:
        target_chat_id = user_group_mapping[user_id]

    if user_id not in ADMINS:
        context.bot.send_message(
            chat_id=target_chat_id,
            text=" У вас нет прав для использования этой команды."
        )
        return

    if not update.message.reply_to_message:
        context.bot.send_message(
            chat_id=target_chat_id,
            text="⚠️ Чтобы размутить, отвечайте на сообщение пользователя."
        )
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
            chat_id=target_chat_id,
            user_id=user_to_unmute.id,
            permissions=permissions
        )

        if target_chat_id in muted_users and user_to_unmute.id in muted_users[target_chat_id]:
            del muted_users[target_chat_id][user_to_unmute.id]
            if not muted_users[target_chat_id]:
                del muted_users[target_chat_id]

        context.bot.send_message(
            chat_id=target_chat_id,
            text=f"🔊 Пользователь @{user_to_unmute.username or user_to_unmute.first_name} размучен."
        )
    except Exception as e:
        context.bot.send_message(
            chat_id=target_chat_id,
            text=f"❌ Ошибка: {e}"
        )

def mutlist_handler(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    chat_type = update.effective_chat.type
    chat_id = update.effective_chat.id

    # Визначаємо, куди надсилати відповідь
    target_chat_id = chat_id
    if chat_type == "private" and user_id in user_group_mapping:
        target_chat_id = user_group_mapping[user_id]

    if target_chat_id not in muted_users or not muted_users[target_chat_id]:
        context.bot.send_message(
            chat_id=target_chat_id,
            text=" На данный момент нет замученных пользователей в этом чате."
        )
        return

    message = "📋 Список замученных пользователей:\n"
    for user_id, info in muted_users[target_chat_id].items():
        time_remaining = format_time_remaining(info['until_date'])
        message += f"👤 @{info['username']} — до {time_remaining}\nПричина: {info['reason']}\n"

    context.bot.send_message(
        chat_id=target_chat_id,
        text=message
    )

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start_handler))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, message_handler))
    dp.add_handler(CommandHandler("mut", mute_handler))
    dp.add_handler(CommandHandler("unmut", unmute_handler))
    dp.add_handler(CommandHandler("mutlist", mutlist_handler))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
