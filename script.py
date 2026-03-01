import telebot
import sqlite3


token = 'token-botfather'
bot = telebot.TeleBot(token)
user_data = {}
ADMIN_ID = 6415054214



conn = sqlite3.connect('anketa.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users ( id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, name TEXT, age TEXT, city TEXT, about TEXT)''')
conn.commit()

@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    item = telebot.types.KeyboardButton("Заполнить анкету")
    markup.add(item)
    bot.send_message(message.chat.id, "Привет, Хочешь запелнить анкету?", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == 'Заполнить анкету')
def fill_form(message):
    user_data[message.chat.id] = {}
    bot.send_message(message.chat.id, "Как тебя зовут?")
    bot.register_next_step_handler(message, ask_name)

def ask_name(message):
    user_data[message.chat.id]["name"] = message.text
    bot.send_message(message.chat.id, "сколько тебе лет?")
    bot.register_next_step_handler(message, ask_age)

def ask_age(message):
    user_data[message.chat.id]["age"] = message.text
    bot.send_message(message.chat.id, "Из какого ты города?")
    bot.register_next_step_handler(message, ask_city)

def ask_city(message):
    user_data[message.chat.id]["city"] = message.text
    bot.send_message(message.chat.id, "Росскажи немного о себе.")
    bot.register_next_step_handler(message, ask_about)

def ask_about(message):
    user_data[message.chat.id]["about"] = message.text
    save_to_db(message.chat.id)
    bot.send_message(message.chat.id, " Спосибо за заполнение анкеты!")

def save_to_db(chat_id):
    data = user_data[chat_id]
    cursor.execute('''INSERT INTO users (user_id, name, age, city, about) VALUES (?, ?, ?, ?, ?)''',
                   (chat_id, data['name'], data['age'], data['city'], data['about']))
    conn.commit()

@bot.message_handler(commands=['get_data'])
def get_data(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "У тебя нет доступа к этой команде.")
        return
    cursor.execute("SELECT name, age, city, about FROM users")
    rows = cursor.fetchall()

    if not rows:
        bot.send_message(message.chat.id, "Нет данных")
        return

    text = ""
    for row in rows:
        name, age, city, about = row
        text += f"Имя: {name}\пВозраст:{age}\пГород: {city}\n0 себе: {about}\n{'-'*20}\n"

    for i in range(0, len(text), 4096):
        bot.send_message(message.chat.id, text[i:i+4096])

bot.polling(none_stop=True)