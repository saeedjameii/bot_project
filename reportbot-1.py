import os
import json
import jdatetime
import pandas as pd
import schedule
import time
import threading
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Load bot token securely from environment variables
BOT_TOKEN = "7854548836:AAEQ_MoIITV5whtmYUCN9JX5sAA0dwljTIs"
if not BOT_TOKEN:
    raise ValueError(
        "Telegram Bot Token is not set. Please set TELEGRAM_BOT_TOKEN as an environment variable."
    )
bot = telebot.TeleBot(BOT_TOKEN)

# File paths
JSON_FILE = os.path.join(os.getcwd(), "user_reports.json")
USERS_FILE = os.path.join(os.getcwd(), "users2.json")
EXCEL_FILE = os.path.join(os.getcwd(), "user_reports.xlsx")
CSV_FILE = os.path.join(os.getcwd(), "user_reports.csv")

# Correct codes for user authentication
USER_CODES = {
    "خانم شفق": "5047",
    "خانم ماهرنیا": "3012",
    "خانم تقی پور": "3024",
    "آقای متین": "3035",
    "آقای شناور": "3041",
    "آقای لواسانی": "3053",
    "آقای جان بخش": "3069",
    "آقای ابراهیمی": "4082",
    "آقای شکیبی": "4071",
}

Manager = ["آقای شناور"]

# Thread lock for file operations
file_lock = threading.Lock()

PRIORITY_LEVELS = ["1", "2", "3", "4", "5"]


# Check and create files if they don't exist
def initialize_files():
    if not os.path.exists(JSON_FILE):
        with open(JSON_FILE, "w", encoding="utf-8") as file:
            json.dump([], file, ensure_ascii=False, indent=4)
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w", encoding="utf-8") as file:
            json.dump([], file, ensure_ascii=False, indent=4)
    if not os.path.exists(EXCEL_FILE):
        pd.DataFrame([]).to_excel(EXCEL_FILE, index=False, engine="openpyxl")


initialize_files()


# Function to save report to JSON
def save_to_json(chat_id, report, file_url=None, user_name=None):
    with file_lock:
        try:
            with open(JSON_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
        except FileNotFoundError:
            data = []
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as file:
                users = json.load(file)
        except FileNotFoundError:
            users = []
        try:
            # Fetch user information
            user_info = bot.get_chat(chat_id)

            # Extract username or fallback to first name
            user_name = (
                user_info.username if user_info.username else user_info.first_name
            )

        except Exception as e:
            print(f"Error fetching user info: {e}")
            user_name = None

        current_date = jdatetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        for user in users:
            if user["chat_id"] == chat_id:
                name = user["name"]

        if file_url:
            my_user = None
            for user in data:
                if user["chat_id"] == chat_id:
                    my_user = user
            my_user["file_urls"].append(file_url)
        else:
            new_entry = {
                "chat_id": chat_id,
                "user_name": user_name,
                "name": name,
                "report": report,
                "date": current_date,
                "file_urls": [],
            }
            data.append(new_entry)

        with open(JSON_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

        # save_user(chat_id)


def save_user(chat_id):
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, "r", encoding="utf-8") as file:
                users = json.load(file)
        else:
            users = []

        if chat_id not in users:
            users.append(chat_id)

        with open(USERS_FILE, "w", encoding="utf-8") as file:
            json.dump(users, file, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error in save_user: {e}")


def save_user_name(chat_id, name):
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, "r", encoding="utf-8") as file:
                users = json.load(file)
        else:
            users = []
        if os.path.exists(JSON_FILE):
            with open(JSON_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
        else:
            data = []
        try:
            # Fetch user information
            user_info = bot.get_chat(chat_id)

            # Extract username or fallback to first name
            user_name = (
                user_info.username if user_info.username else user_info.first_name
            )

        except Exception as e:
            print(f"Error fetching user info: {e}")
            user_name = None

        users.append({"chat_id": chat_id, "name": name, "user_name": user_name})

        with open(USERS_FILE, "w", encoding="utf-8") as file:
            json.dump(users, file, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error in save_user_name: {e}")


# Save data to csv
def json_to_csv():
    with file_lock:
        try:
            with open(JSON_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
        except FileNotFoundError:
            data = []

    df = pd.DataFrame(data)
    column_order = ["chat_id", "user_name", "name", "report", "date", "file_urls"]

    # Retry mechanism to handle file access issues
    for attempt in range(3):  # Retry 3 times
        try:
            df.to_csv(CSV_FILE, columns=column_order, index=False, encoding="utf-8-sig")
            print(f"CSV file saved successfully at {CSV_FILE}")
            break
        except Exception as e:
            print(f"Error saving to CSV (Attempt {attempt + 1}/3): {e}")
            if attempt < 2:  # Don't sleep after the last attempt
                time.sleep(2)  # Wait 2 seconds before retrying
            else:
                print(
                    f"Failed to save CSV after 3 attempts. Please check the file: {CSV_FILE}"
                )


def save_to_excel():
    with file_lock:
        try:
            with open(JSON_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
        except FileNotFoundError:
            data = []

    df = pd.DataFrame(data)
    column_order = ["chat_id", "user_name", "name", "report", "date", "file_urls"]

    # Retry mechanism to handle file access issues
    for attempt in range(3):  # Retry 3 times
        try:
            df.to_excel(
                EXCEL_FILE, columns=column_order, index=False, engine="openpyxl"
            )
            print(f"Excel file saved successfully at {EXCEL_FILE}")
            break
        except Exception as e:
            print(f"Error saving to Excel (Attempt {attempt + 1}/3): {e}")
            if attempt < 2:  # Don't sleep after the last attempt
                time.sleep(2)  # Wait 2 seconds before retrying
            else:
                print(
                    f"Failed to save Excel after 3 attempts. Please check the file: {EXCEL_FILE}"
                )


# /start command handler
@bot.message_handler(commands=["start"])
def welcome(message):
    bot.send_message(message.chat.id, "به ربات تداوم خرد پژوهان کاسپین خوش آمدید.")
    bot.send_message(
        message.chat.id, "لطفا کد کاربری خود را وارد کنید.(کیبورد انگلیسی)"
    )


@bot.message_handler(func=lambda message: True)
def check_code_or_report(message):
    # Check if the entered code matches any user code
    entered_code = message.text
    user_name = None
    for name, code in USER_CODES.items():
        if entered_code == code:
            user_name = name
            break

    if user_name:
        save_user_name(message.chat.id, user_name)
        if user_name in Manager:
            bot.send_message(
                message.chat.id, f"{user_name} عزیز، خوش آمدید! شما مدیر هستید."
            )
            bot.send_message(
                message.chat.id,
                "لطفا یکی از گزینه‌های زیر را انتخاب کنید:",
                reply_markup=manager_menu(),
            )
        else:
            bot.send_message(message.chat.id, f"{user_name} عزیز، خوش آمدید!")
            bot.send_message(
                message.chat.id,
                "لطفا یکی از گزینه‌های زیر را انتخاب کنید:",
                reply_markup=main_menu(),
            )
    else:
        bot.send_message(message.chat.id, "کد اشتباه است. لطفا دوباره امتحان کنید.")


@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    chat_id = call.message.chat.id
    if call.data == "send_report":
        today_date = jdatetime.datetime.now().strftime("%Y/%m/%d")
        bot.send_message(chat_id, f"لطفا گزارش تاریخ {today_date} خود را ارسال کنید.")
        bot.register_next_step_handler(call.message, get_report)
    elif call.data == "other_services":
        bot.send_message(chat_id, "این گزینه در آپدیت‌های بعدی اضافه می‌شود.")
    elif call.data == "send_command":
        bot.send_message(chat_id, "لطفا دستور خود را وارد کنید:")
        bot.register_next_step_handler(call.message, get_command)
    elif call.data == "view_reports":
        json_to_csv()
        bot.send_document(chat_id, open(CSV_FILE, "rb"))
    elif call.data == "yes":
        bot.send_message(chat_id, "لطفا فایل یا عکس خود را ارسال کنید.")
        bot.register_next_step_handler(call.message, handle_file)
    elif call.data == "no":
        bot.send_message(
            chat_id,
            f"گزارش شما با موفقیت در {jdatetime.datetime.now().strftime('%H:%M')} ثبت شد.",
        )
        bot.send_message(
            chat_id,
            "لطفا یکی از گزینه‌های زیر را انتخاب کنید:",
            reply_markup=main_menu(),
        )


def get_command(message):
    chat_id = message.chat.id
    command = message.text
    bot.send_message(chat_id, "لطفا درجه اهمیت دستور را مشخص کنید:", reply_markup=priority_menu())
    bot.register_next_step_handler(message, lambda msg: get_priority(msg, command))

def get_priority(message, command):
    priority = message.text.strip()

    if priority not in PRIORITY_LEVELS:
        bot.send_message(message.chat.id, "درجه اهمیت نامعتبر است. لطفا مجددا انتخاب کنید.")
        bot.send_message(message.chat.id, "لطفا درجه اهمیت دستور را مشخص کنید:", reply_markup=priority_menu())
        return

    # مرحله بعد: دریافت مهلت
    bot.send_message(message.chat.id, "لطفا مهلت انجام دستور را وارد کنید:")
    bot.register_next_step_handler(message, lambda msg: get_deadline(msg, command, priority))

def get_deadline(message, command, priority):
    deadline = message.text.strip()

    # مرحله بعد: دریافت نام کاربر هدف
    bot.send_message(message.chat.id, "لطفا نام کاربری که دستور به او ارسال می‌شود را وارد کنید:")
    bot.register_next_step_handler(message, lambda msg: send_command_to_user(msg, command, priority, deadline))


def send_command_to_user(message, command, priority, deadline):
    target_user_name = message.text.strip()
    target_chat_id = None

    try:
        with open(USERS_FILE, "r", encoding="utf-8") as file:
            users = json.load(file)

        for user in users:
            if user["name"] == target_user_name:
                target_chat_id = user["chat_id"]
                break

        if target_chat_id:
            bot.send_message(
                target_chat_id,
                f"دستور مدیر: {command}\nدرجه اهمیت: {priority}\nمهلت: {deadline}",
            )
            bot.send_message(message.chat.id, "دستور با موفقیت ارسال شد.")
        else:
            bot.send_message(message.chat.id, "کاربر مورد نظر پیدا نشد. لطفا مجددا تلاش کنید.")
    except Exception as e:
        print(f"خطا در ارسال دستور: {e}")
        bot.send_message(message.chat.id, "خطا در پردازش درخواست.")




def get_report(message):
    report = message.text
    chat_id = message.chat.id
    entered_code = message.text
    user_name = None
    for name, code in USER_CODES.items():
        if entered_code == code:
            user_name = name
            break
    save_to_json(chat_id, report, user_name=user_name)

    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("بله", callback_data="yes"),
        InlineKeyboardButton("خیر", callback_data="no"),
    )
    bot.send_message(
        chat_id, "آیا می‌خواهید فایلی اضافه بر گزارش بفرستید؟", reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("priority_"))
def handle_priority_selection(call):
    chat_id = call.message.chat.id
    priority = call.data.split("_")[1]  # استخراج مقدار اولویت (مانند "1", "2", ...)
    command = call.message.text.split(":", 1)[1].strip()  # فرض می‌کنیم دستور قبلاً ارسال شده

    bot.send_message(chat_id, "لطفا مهلت انجام دستور را وارد کنید:")
    bot.register_next_step_handler(call.message, lambda msg: get_deadline(msg, command, priority))


@bot.message_handler(content_types=["document", "photo"])
def handle_file(message):
    chat_id = message.chat.id
    if message.document:
        file_id = message.document.file_id
        file_name = message.document.file_name
    elif message.photo:
        file_id = message.photo[-1].file_id
        file_name = "photo.jpg"
    else:
        bot.send_message(chat_id, "خطا: لطفا فقط فایل یا عکس ارسال کنید.")
        return

    try:
        file_info = bot.get_file(file_id)
        file_url = f"https://api.telegram.org/file/bot{bot.token}/{file_info.file_path}"
        # Retrieve user name based on chat_id and entered code
        entered_code = message.text
        user_name = None
        for name, code in USER_CODES.items():
            if entered_code == code:
                user_name = name
                break
        save_to_json(chat_id, "گزارش با فایل دریافت شده", file_url, user_name=user_name)
        bot.send_message(chat_id, "گزارش شما با موفقیت ثبت شد.")
        bot.send_message(
            chat_id,
            "لطفا یکی از گزینه‌های زیر را انتخاب کنید:",
            reply_markup=main_menu(),
        )
    except Exception as e:
        print(f"خطا در ذخیره فایل: {e}")
        bot.send_message(chat_id, "خطا در پردازش فایل.")

def priority_menu():
    markup = InlineKeyboardMarkup()
    for priority in PRIORITY_LEVELS:
        markup.add(InlineKeyboardButton(priority, callback_data=f"priority_{priority}"))
    return markup


def manager_menu():
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("ارسال دستور به کاربر", callback_data="send_command"),
        InlineKeyboardButton("مشاهده گزارش کاربران", callback_data="view_reports"),
    )
    return markup


def main_menu():
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("فرستادن گزارش", callback_data="send_report"),
        InlineKeyboardButton("سایر خدمات", callback_data="other_services"),
    )
    return markup


def send_scheduled_message():
    with file_lock:
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as file:
                users = json.load(file)
        except FileNotFoundError:
            users = []

    for chat_id in users:
        try:
            bot.send_message(
                chat_id,
                "این یک پیام یاد آوریست. کاربر عزیز لطفا گزارش خود را ارسال کنید",
            )
        except Exception as e:
            print(f"خطا در ارسال پیام به {chat_id}: {e}")


schedule.every().day.at("19:00").do(send_scheduled_message)
schedule.every(30).seconds.do(json_to_csv)
schedule.every(30).seconds.do(save_to_excel)


def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)


# Reconnection loop for bot polling
def run_bot():
    while True:
        try:
            bot.polling()
        except Exception as e:
            print(f"Bot polling error: {e}")
            time.sleep(5)  # Try reconnecting every 5 seconds


if __name__ == "__main__":
    threading.Thread(target=run_scheduler, daemon=True).start()
    run_bot()  # Call the bot polling in a loop to ensure it reconnects if it stops
