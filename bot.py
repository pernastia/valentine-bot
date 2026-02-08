import json
import os
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters
)
import os

TOKEN = os.getenv("TOKEN")

ASK_USERNAME, ASK_TEXT = range(2)

USERS_FILE = "users.json"
VALENTINES_FILE = "valentines.json"


# ----------------- РОБОТА З ФАЙЛАМИ -----------------
def load_data(filename):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_data(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ----------------- КНОПКИ -----------------
def main_menu():
    keyboard = [
        ["💌 Надіслати валентинку"],
        ["📥 Мої валентинки", "ℹ️ Як це працює"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def after_send_menu():
    keyboard = [
        ["💌 Ще валентинку"],
        ["⬅️ Головне меню"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def back_menu():
    keyboard = [["⬅️ Головне меню"]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# ----------------- START -----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if not user.username:
        await update.message.reply_text(
            "Щоб отримувати валентинки, потрібно встановити @username у налаштуваннях Telegram ⚙️\n\n"
            "Після цього знову натисни /start 💖"
        )
        return

    users = load_data(USERS_FILE)
    users[user.username.lower()] = update.effective_chat.id
    save_data(USERS_FILE, users)

    await update.message.reply_text(
        "Привіт 💖\n"
        "Це бот анонімних валентинок. Тут можна таємно надіслати комусь приємне зізнання або отримати валентинку самому(самій) 😌\n\n"
        "Обирай дію нижче 👇",
        reply_markup=main_menu()
    )


# ----------------- ГОЛОВНЕ МЕНЮ -----------------
async def menu_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "💌 Надіслати валентинку" or text == "💌 Ще валентинку":
        await update.message.reply_text(
            "Кому ти хочеш надіслати валентинку?\n"
            "Введи @username людини (наприклад: @alexlove) 💘",
            reply_markup=ReplyKeyboardRemove()
        )
        return ASK_USERNAME

    elif text == "📥 Мої валентинки":
        await show_valentines(update, context)

    elif text == "ℹ️ Як це працює":
        await update.message.reply_text(
            "💘 Як працює бот валентинок:\n\n"
            "• Ти можеш надіслати валентинку будь-кому, знаючи лише їхній @username\n"
            "• Повідомлення приходять повністю анонімно\n"
            "• Якщо людина ще не заходила в бота — валентинка збережеться і прийде пізніше\n"
            "• Ніхто не дізнається, хто саме її надіслав 🤫\n\n"
            "Поширюй трохи тепла ✨",
            reply_markup=back_menu()
        )

    elif text == "⬅️ Головне меню":
        await update.message.reply_text(
            "Обирай, що хочеш зробити далі 💖",
            reply_markup=main_menu()
        )


# ----------------- ПОКАЗ ВАЛЕНТИНОК -----------------
async def show_valentines(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    valentines = load_data(VALENTINES_FILE)
    messages = valentines.get(user.username.lower(), [])

    if messages:
        await update.message.reply_text("У тебе є валентинки 😏💖\nОсь що тобі написали анонімно:")
        for msg in messages:
            await update.message.reply_text(
                f"💌 Тобі анонімна валентинка:\n\n{msg}\n\nВід таємного прихильника(ці) 😌"
            )
        valentines[user.username.lower()] = []
        save_data(VALENTINES_FILE, valentines)
        await update.message.reply_text("Нових валентинок поки немає 🫶", reply_markup=back_menu())
    else:
        await update.message.reply_text(
            "Поки що для тебе немає валентинок 🥺\n\n"
            "Можеш натякнути друзям, щоб написали тобі щось приємне 😌💕",
            reply_markup=back_menu()
        )


# ----------------- ВВІД USERNAME -----------------
async def ask_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.text.strip()

    if not username.startswith("@"):
        await update.message.reply_text(
            "Хмм, це не схоже на @username 🤔\n"
            "Спробуй ще раз у форматі: @username"
        )
        return ASK_USERNAME

    context.user_data["recipient"] = username[1:].lower()

    await update.message.reply_text(
        "Супер ✨\n"
        "Тепер напиши текст валентинки.\n\n"
        "Вона буде повністю анонімною 🤫💖"
    )
    return ASK_TEXT


# ----------------- ЗБЕРЕГТИ ВАЛЕНТИНКУ -----------------
async def save_valentine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    recipient = context.user_data["recipient"]

    users = load_data(USERS_FILE)
    valentines = load_data(VALENTINES_FILE)

    if recipient in users:
        await context.bot.send_message(
            users[recipient],
            f"💌 Тобі анонімна валентинка:\n\n{text}\n\nВід таємного прихильника(ці) 😌"
        )
    else:
        valentines.setdefault(recipient, []).append(text)
        save_data(VALENTINES_FILE, valentines)

    await update.message.reply_text(
        "Готово! Твоя валентинка відправлена 💌\n\n"
        "Якщо отримувач ще не запускав бота — він(вона) отримає її одразу після першого входу 😉\n\n"
        "Хочеш надіслати ще одну?",
        reply_markup=after_send_menu()
    )
    return ConversationHandler.END


# ----------------- CANCEL -----------------
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Окей, скасували відправку ❌\n\nПовертаю тебе в меню",
        reply_markup=main_menu()
    )
    return ConversationHandler.END


# ----------------- ЗАПУСК -----------------
app = ApplicationBuilder().token(TOKEN).build()

conv_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.TEXT & ~filters.COMMAND, menu_router)],
    states={
        ASK_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_text)],
        ASK_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_valentine)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

app.add_handler(CommandHandler("start", start))
app.add_handler(conv_handler)

print("Бот працює 💘")
app.run_polling()


