import telebot
import re
from scheduler import book_timeslot
from telebot_calendar import CallbackData, Calendar
from telebot.types import InlineKeyboardMarkup
import datetime



bot = telebot.TeleBot('6392098825:AAGuk-dTXk-5RJltiXoF1G9uslU2xWfYuoE')

def check_email(email):
    regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
    return re.search(regex, email)


@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    if is_allowed_user(user_id):
        bot.send_message(user_id, "Привет! Я телеграм бот Lessons.kz. Я могу помочь создать событие.")
        bot.send_message(user_id, "Пожалуйста, введите название события:")
        bot.register_next_step_handler(message, get_event_summary)
    else:
        bot.send_message(user_id, "Вы не имеете доступа к данной команде.")

def is_allowed_user(user_id):
    allowed_user_id = '449507321' or 'dsafsd' or 'sdfs'
    return str(user_id) == allowed_user_id


def get_event_summary(message):
    user_id = message.chat.id
    event_summary = message.text
    bot.send_message(user_id, "Пожалуйста, выберите описание события")
    bot.register_next_step_handler(message, get_event_description, event_summary)

def get_event_description(message, event_summary):
    user_id = message.chat.id
    event_description = message.text
    bot.send_message(user_id, "Пожалуйста, выберите дату в формате YYYY-MM-DD")
    bot.register_next_step_handler(message, select_date, event_summary, event_description)

def select_date(message, event_summary, event_description):
    user_id = message.chat.id
    date_time = message.text
    bot.send_message(user_id, "Пожалуйста, выберите время", reply_markup=get_time_keyboard(user_id))
    bot.register_next_step_handler(message, select_time, event_summary, event_description, date_time)
def select_time(message, event_summary, event_description, date_time):
    user_id = message.chat.id
    booking_time = message.text
    if not re.match(r'^\d{2}:\d{2}$', booking_time):
        bot.send_message(user_id, "Введите корректное время в формате HH:MM.", reply_markup=get_time_keyboard(user_id))
        return
    bot.send_message(user_id, "Введите имя преподавателя:", reply_markup=select_prepod_keyboard(user_id))
    bot.register_next_step_handler(message, select_prepod, event_summary, event_description, date_time, booking_time)

def select_prepod(message, event_summary, event_description, date_time, booking_time):
    user_id = message.chat.id
    prepod = message.text
    bot.send_message(user_id, "Введите место проведения урока:", reply_markup=select_location_keyboard(user_id))
    bot.register_next_step_handler(message, select_location, event_summary, event_description, date_time, booking_time, prepod)

def select_location(message, event_summary, event_description, date_time, booking_time, prepod):
    user_id = message.chat.id
    location = message.text
    bot.send_message(user_id, "Введите адрес почты:", reply_markup=get_mail_keyboard(user_id))
    bot.register_next_step_handler(message, select_email, event_summary, event_description, date_time, booking_time, prepod, location)


def select_email(message, event_summary, event_description, date_time, booking_time, prepod, location):
    user_id = message.chat.id
    email = message.text
    if check_email(email):
        bot.send_message(user_id, "Создаю событие...")
        input_email = email
        response = book_timeslot(event_summary, event_description, date_time, booking_time, input_email, prepod, location)
        if response:
            bot.send_message(user_id, f"Событие создано! Время - {date_time} - {booking_time}")
        else:
            bot.send_message(user_id, "Пожалуйста, выберите другое время, так как это уже занято.")
    else:
        bot.send_message(user_id, "Введите корректный адрес почты.")

def get_mail_keyboard(user_id):
    mail = telebot.types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True)
    mail_slots = ['insar@lessons.kz', 'vitaly@lessons.kz', 'etc']
    mail.add(*mail_slots)
    return mail
def get_time_keyboard(user_id):
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=5, one_time_keyboard=True)
    time_slots = [
        '08:00', '08:30', '09:00', '09:30', '10:00', '10:30', '11:00', '11:30',
        '12:00', '12:30', '13:00', '13:30', '14:00', '14:30', '15:00', '15:30',
        '16:00', '16:30', '17:00', '17:30', '18:00', '18:30', '19:00', '19:30',
        '20:00', '20:30', '21:00', '21:30', '22:00', '22:30', '23:00', '23:30', '00:00'
    ]
    keyboard.add(*time_slots)
    return keyboard
def select_location_keyboard(user_id):
    loc = telebot.types.ReplyKeyboardMarkup(row_width=3, one_time_keyboard=True)
    loc_slots = ['Тэта', 'Омега', 'Дельта', 'Сигма', 'Гамма', 'Омикрон', 'дистанционно']
    loc.add(*loc_slots)
    return loc

def select_prepod_keyboard(user_id):
    pr = telebot.types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True)
    pr_slots = ['Инсар', 'Виталий', 'etc']
    pr.add(*pr_slots)
    return pr

calendar_callback = CallbackData("calendar", "action", "year", "month", "day")

calendar = Calendar()

def send_calendar(message):
    now = datetime.datetime.now()
    markup = calendar.create_calendar(
        name=calendar_callback.prefix,
        year=now.year,
        month=now.month,
    )
    bot.send_message(
        message.chat.id,
        "Выберите дату:",
        reply_markup=markup,
    )


@bot.message_handler(commands=['select_date'])
def select_date_command(message):
    user_id = message.chat.id
    if is_allowed_user(user_id):
        send_calendar(message)
    else:
        bot.send_message(user_id, "Вы не имеете доступа к данной команде.")

@bot.callback_query_handler(func=calendar_callback.filter())
def handle_calendar(callback):
    if callback.data:
        action = callback.data["action"]
        year = int(callback.data["year"])
        month = int(callback.data["month"])
        day = int(callback.data["day"])

        if action == "DAY":
            selected_date = datetime.date(year, month, day)

            bot.send_message(callback.from_user.id, f"Вы выбрали дату: {selected_date}")
        elif action == "CANCEL":
            bot.send_message(callback.from_user.id, "Выбор даты отменен.")

if __name__ == "__main__":
    bot.polling()
