from telegram import Update, ChatPermissions, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
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
user_group_mapping = {-1002553267167}  # {user_id: group_chat_id}

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
            user_group_mapping[user_id] = update.effective_chat.id
            update.message.reply_text(f"@{username}, я отправил вам команды в личные сообщения!")
            
            is_admin = user_id in ADMINS
            participant_commands = [
                [KeyboardButton("калл"), KeyboardButton("/mutlist")]
            ]
            admin_commands = participant_commands + [
                [KeyboardButton("/mut"), KeyboardButton("/unmut")]
            ]
            keyboard = admin_commands if is_admin else participant_commands
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

            context.bot.send_message(
                chat_id=user_id,
                text="Выберите команду:",
                reply_markup=reply_markup
            )
        except Exception as e:
            update.message.reply_text(f"⚠️ Не удалось отправить сообщение в личный чат. Пожалуйста, начните диалог со мной, написав /start в личных сообщениях.\nОшибка: {e}")
        return

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
    text = update.message.text.strip().lower()

    # Перевіряємо, чи користувач вводить тривалість мута
    if chat_type == "private" and 'mut_user' in context.user_data:
        duration_str = update.message.text.strip()
        duration_seconds = parse_duration(duration_str)
        if duration_seconds == 0:
            update.message.reply_text("⚠️ Неверный формат длительности. Пример: 1h, 30m, 5d")
            return

        context.user_data['duration'] = duration_str
        context.user_data['duration_seconds'] = duration_seconds
        update.message.reply_text("Введите причину мута:")
        context.user_data['step'] = 'reason'
        return

    # Перевіряємо, чи користувач вводить причину мута
    if chat_type == "private" and context.user_data.get('step') == 'reason':
        reason = update.message.text.strip()
        user_to_mute_id = context.user_data['mut_user']
        duration_str = context.user_data['duration']
        duration_seconds = context.user_data['duration_seconds']
        target_chat_id = user_group_mapping.get(user_id)

        try:
            user_to_mute = context.bot.get_chat_member(target_chat_id, user_to_mute_id).user
            until_date = datetime.utcnow() + timedelta(seconds=duration_seconds)
            permissions = ChatPermissions(can_send_messages=False)

            context.bot.restrict_chat_member(
                chat_id=target_chat_id,
                user_id=user_to_mute_id,
                permissions=permissions,
                until_date=until_date
            )

            if target_chat_id not in muted_users:
                muted_users[target_chat_id] = {}
            muted_users[target_chat_id][user_to_mute_id] = {
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
                            user_id=user_to_mute_id,
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
                        if target_chat_id in muted_users and user_to_mute_id in muted_users[target_chat_id]:
                            del muted_users[target_chat_id][user_to_mute_id]
                            if not muted_users[target_chat_id]:
                                del muted_users[target_chat_id]
                    except Exception as e:
                        print(f"❌ Ошибка авторазмута: {e}")
                Timer(duration_seconds, unmute_later).start()

            # Очищаємо стан
            context.user_data.clear()
        except Exception as e:
            update.message.reply_text(f"❌ Ошибка при муте: {e}")
            context.user_data.clear()
        return

    # Обробка команди "калл"
    if text.startswith("калл"):
        target_chat_id = chat_id
        if chat_type == "private" and user_id in user_group_mapping:
            target_chat_id = user_group_mapping[user_id]

        now = time.time()
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

    target_chat_id = chat_id
    if chat_type == "private" and user_id in user_group_mapping:
        target_chat_id = user_group_mapping[user_id]

    if user_id not in ADMINS:
        context.bot.send_message(
            chat_id=target_chat_id,
            text=" У вас нет прав для использования этой команды."
        )
        return

    # Отримуємо список учасників із USER_LIST
    potential_members = USER_LIST.splitlines()
    if not potential_members:
        context.bot.send_message(
            chat_id=target_chat_id,
            text="Список участников пуст."
        )
        return

    # Формуємо інлайн-клавіатуру з ніками
    buttons = []
    for member in potential_members:
        member = member.strip()
        if member:
            # Оскільки у нас немає ID у USER_LIST, ми будемо використовувати сам нік як ідентифікатор
            # Але для коректної роботи мута нам потрібно знати ID, тому це обмеження
            # Для спрощення припустимо, що нік унікальний, але мутити ми будемо вручну через ID
            buttons.append([InlineKeyboardButton(member, callback_data=f"mut_{member}")])

    reply_markup = InlineKeyboardMarkup(buttons)
    context.bot.send_message(
        chat_id=target_chat_id,
        text="Выберите участника для мута:",
        reply_markup=reply_markup
    )

def unmute_handler(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    chat_type = update.effective_chat.type
    chat_id = update.effective_chat.id

    target_chat_id = chat_id
    if chat_type == "private" and user_id in user_group_mapping:
        target_chat_id = user_group_mapping[user_id]

    if user_id not in ADMINS:
        context.bot.send_message(
            chat_id=target_chat_id,
            text=" У вас нет прав для использования этой команды."
        )
        return

    if target_chat_id not in muted_users or not muted_users[target_chat_id]:
        context.bot.send_message(
            chat_id=target_chat_id,
            text=" На данный момент нет замученных пользователей в этом чате."
        )
        return

    # Формуємо інлайн-клавіатуру з замученими користувачами
    buttons = []
    for user_id, info in muted_users[target_chat_id].items():
        buttons.append([InlineKeyboardButton(f"@{info['username']}", callback_data=f"unmut_{user_id}")])

    reply_markup = InlineKeyboardMarkup(buttons)
    context.bot.send_message(
        chat_id=target_chat_id,
        text="Выберите участника для размута:",
        reply_markup=reply_markup
    )

def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    user_id = query.from_user.id
    target_chat_id = user_group_mapping.get(user_id)
    if not target_chat_id:
        query.message.reply_text("Ошибка: группа не найдена.")
        return

    data = query.data
    action, identifier = data.split("_", 1)

    if action == "mut":
        # Для мута ми не можемо отримати ID із USER_LIST, тому попросимо адміна ввести ID вручну
        query.message.reply_text(f"Вы выбрали {identifier}. Введите ID пользователя (можно узнать через @userinfobot):")
        context.user_data['mut_nickname'] = identifier
        context.user_data['step'] = 'mut_id'
        return

    if action == "unmut":
        user_to_unmute_id = int(identifier)
        try:
            user_to_unmute = context.bot.get_chat_member(target_chat_id, user_to_unmute_id).user
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
                user_id=user_to_unmute_id,
                permissions=permissions
            )

            if target_chat_id in muted_users and user_to_unmute_id in muted_users[target_chat_id]:
                del muted_users[target_chat_id][user_to_unmute_id]
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
    dp.add_handler(CallbackQueryHandler(button_handler))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
