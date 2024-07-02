"""
23.05.2023

"""
import telebot
import random
import datetime
from variants import Variants
from telebot import types
import requests
import json
from geopy.geocoders import Nominatim
import certifi
import ssl
import geopy.geocoders

token = '' #bot token from @BotFather

bot = telebot.TeleBot(token)
storage = dict()

def init_storage(user_id):
    storage[user_id] = dict(attempt=None, random_digit=None)

def set_data_storage(user_id, key, value):
    storage[user_id][key] = value

def get_data_storage(user_id):
    return storage[user_id]

@bot.message_handler(commands=['start', 'help'] )
def welcome(message):
    sti = open('static/hi.webp', 'rb')
    bot.send_sticker(message.chat.id, sti)

    bot.send_message(message.chat.id,
                     "Добро пожаловать, {0.first_name}!\nЯ - <b>{1.first_name}</b>, бот дурачок (а может и не совсем ."
                     "Я почти ничего не умею. А то что умею - абсолютно бесполезно. Но ты можешь просто потыкать на кнопочки и псомотреть, что будет. \n/button - вызов кнопок.\n"
                     "/help - то же что и Старт\n/switch - Отправить меня в друиге чаты\n"
                     "/random - я назову тебе рандомное число от 1 до 100)))".format(message.from_user, bot.get_me()),
                     parse_mode='html')

@bot.message_handler(commands=['switch'])
def switch(message):
    markup = types.InlineKeyboardMarkup()
    switch_button = types.InlineKeyboardButton('Try', switch_inline_query="")
    markup.add(switch_button)
    bot.send_message(message.chat.id, "Выбрать чат", reply_markup=markup)

@bot.message_handler(commands=['button'])
def button_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Игра Камень, ножницы, бумага")
    item2 = types.KeyboardButton("Поговорим?")
    item3 = types.KeyboardButton("Отправить Настюше мем")
    item4 = types.KeyboardButton("Повторюшка")
    item5 = types.KeyboardButton("Игра Угадай число")
    item6 = types.KeyboardButton("Расскажи о погоде")

    markup.add(item1, item2, item3, item4, item5, item6)
    bot.send_message(message.chat.id, 'Выберите что-нибудь', reply_markup=markup)

@bot.message_handler(commands=['random'])
def rand(message):
    bot.send_message(message.chat.id, str(random.randint(0, 100)))


@bot.message_handler(func=lambda message: message.text == "Расскажи о погоде")
def weather(message):
    bot.send_message(message.chat.id, "Введите город!")
    bot.register_next_step_handler(message, town)

def town (message):
  try:
    ctx = ssl._create_unverified_context(cafile=certifi.where())
    geopy.geocoders.options.default_ssl_context = ctx
    loc = Nominatim(user_agent="GetLoc", scheme='http')
    # entering the location name
    getLoc = loc.geocode(message.text)

    print(getLoc.address)
    print("Latitude = ", getLoc.latitude, "\n")
    print("Longitude = ", getLoc.longitude)

    url = f'https://api.weather.yandex.ru/v1/informers?lat={getLoc.latitude}&lon={getLoc.longitude}'
    headers = {"X-Yandex-API-Key": "00a31362-0dff-45c4-bb41-9895dd3235c5"}
    getLoc = loc.geocode(message.text)
    r = requests.get(url=url, headers=headers)
    bot.send_message(message.chat.id, r.text)
    if r.status_code == 200:
      data = json.loads(r.text)
      fact = data["fact"]
      forecast = data["forecast"]
      bot.send_message(message.chat.id,
                       text=f'Сейчас в городе {getLoc} {fact["temp"]}°, ощущается как {fact["feels_like"]}°. Сейчас на улице {fact["condition"]}. Скорость ветра: {fact["wind_speed"]}.'f'"Восход: {forecast["sunrise"]}. Закат: {forecast["sunset"]}')
    else:
      bot.send_message(message.chat.id, 'Проблемы в weather API')
  except Exception as e:
    bot.send_message(message.chat.id, "Я не знаю такой город")


@bot.message_handler(func=lambda message: message.text == "Игра Камень, ножницы, бумага")
def knb_games(message):
    init_storage(message.chat.id)

    attempt = 4
    us = 0
    bt = 0
    set_data_storage(message.chat.id, "attempt", attempt)
    set_data_storage(message.chat.id, "us", us)
    set_data_storage(message.chat.id, "bt", bt)

    bot.send_message(message.chat.id, f'Игра "Камень, ножницы, бумага"! Играем до трех попыток')
    rand = random.choice(list(Variants))
    print(rand.value)

    set_data_storage(message.chat.id, "random_digit", rand)
    print(get_data_storage(message.chat.id))

    bot.send_message(message.chat.id, "Готово! Загадан один из вариантов!")
    bot.send_message(message.chat.id, "Введите слово Камень, ножницы или бумага")
    bot.register_next_step_handler(message, process_knb_step)

def process_knb_step(message):
    us_digit = message.text

    attempt = get_data_storage(message.chat.id)["attempt"]
    us = get_data_storage(message.chat.id)["us"]
    bt = get_data_storage(message.chat.id)["bt"]
    rand = get_data_storage(message.chat.id)["random_digit"]

    if attempt >= 1:
        if us_digit.lower() == rand.value.lower():
            bot.send_message(message.chat.id, f'Ничья! Я загадал: {rand.value}\n Счет {us}:{bt}')
            attempt-=1

        elif us_digit.lower() == 'камень':
            if rand == Variants.PAPER:
                bt+=1
                bot.send_message(message.chat.id, f'Ты проиграл! Я загадал {rand}\n Счет {us}:{bt}')
                attempt -= 1
            else:
                us+=1
                bot.send_message(message.chat.id, f'Ты победил! Я загадал {rand}\n Счет {us}:{bt}')
                attempt -= 1
        elif us_digit.lower() == 'бумага':
            if rand == Variants.ROCK:
                us+=1
                bot.send_message(message.chat.id, f'Ты победил! Я загадал {rand}\n Счет {us}:{bt}')
                attempt -= 1
            else:
                bt+=1
                bot.send_message(message.chat.id, f'Ты проиграл! Я загадал {rand}\n Счет {us}:{bt}')
                attempt -= 1
        elif us_digit.lower() == 'ножницы':
            if rand == Variants.PAPER:
                us+=1
                bot.send_message(message.chat.id, f'Ты победил! Я загадал {rand}\n Счет {us}:{bt}')
                attempt -= 1
            else:
                bt+=1
                bot.send_message(message.chat.id, f'Ты проиграл! Я загадал {rand}\n Счет {us}:{bt}')
                attempt -= 1
        if attempt == 1:
            bot.send_message(message.chat.id, f'Игра окончена, счет {us}:{bt}')
            if us > bt:
                bot.send_message(message.chat.id, "Ты выиграл этот бой!")
            elif us < bt:
                bot.send_message(message.chat.id, "Увы, ты проиграл!")
            else:
                bot.send_message(message.chat.id, "Мы так ничего и не решили!")
            init_storage(message.chat.id)
            return

        set_data_storage(message.chat.id, "attempt", attempt)
        set_data_storage(message.chat.id, "us", us)
        set_data_storage(message.chat.id, "bt", bt)

        rand = random.choice(list(Variants))
        print(rand.value)

        set_data_storage(message.chat.id, "random_digit", rand)
        print(get_data_storage(message.chat.id))

        bot.send_message(message.chat.id, "Еще попытка!")
        bot.register_next_step_handler(message, process_knb_step)


@bot.message_handler(func=lambda message: message.text == "Отправить Настюше мем")
def mem(message):
    markup = types.InlineKeyboardMarkup()
    item3 = types.InlineKeyboardButton("Отправить", url='https://t.me/nnastyavas', callback_data='send')
    markup.add(item3)
    bot.send_message(message.chat.id, 'Нажми', reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Поговорим?")
def talk(message):
    bot.send_message(message.chat.id, "Давай! Но это будет не самый длинный диалог. Я еще не знаю много слов. Что ты хочешь знать? ")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    mar = types.KeyboardButton("Как дела?")
    mar2 = types.KeyboardButton("Подскажи время")
    markup.add(mar, mar2)
    bot.send_message(message.chat.id, "Задайте вопрос.", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "Как дела?")
def lala(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    item1 = types.InlineKeyboardButton("Хорошо", callback_data='good')
    item2 = types.InlineKeyboardButton("Пока не родила", callback_data='soso')
    markup.add(item1, item2)
    bot.send_message(message.chat.id, "Отлично, сам как?", reply_markup=markup)
    #bot.send_message(message.chat.id, "Я не знаю, что тебе ответить")

@bot.message_handler(func=lambda message: message.text == "Подскажи время")
def timxe(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    item1 = types.InlineKeyboardButton("Дата", callback_data='date')
    item2 = types.InlineKeyboardButton("Время", callback_data='time')
    markup.add(item1, item2)
    bot.send_message(message.chat.id, "Это я знаю!", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Игра Угадай число")
def digitgames(message):
    init_storage(message.chat.id)

    attempt = 5
    set_data_storage(message.chat.id, "attempt", attempt)

    bot.send_message(message.chat.id, f'Игра "Угадай число"! Количество попыток: {attempt}')
    rand = random.randint(1, 10)
    print(rand)

    set_data_storage(message.chat.id, "random_digit", rand)
    print(get_data_storage(message.chat.id))

    bot.send_message(message.chat.id, "Готово! Загадано число от 1 до 10!")
    bot.send_message(message.chat.id, "Введите число")
    bot.register_next_step_handler(message, process_digit_step)

def process_digit_step(message):
    user_digit = message.text

    if not user_digit.isdigit():
        msg = bot.reply_to(message, "Вы ввели не цифры, введите пожалуйста цифры!")
        bot.register_next_step_handler(msg, process_digit_step)
        return
    attempt = get_data_storage(message.chat.id)["attempt"]
    rand = get_data_storage(message.chat.id)["random_digit"]

    if int(user_digit) == rand:
        bot.send_message(message.chat.id, f'Ура! Ты угадал число! Это была цифра: {rand}')
        init_storage(message.chat.id)
        return
    elif attempt > 1:
        attempt-=1
        set_data_storage(message.chat.id, "attempt", attempt)
        bot.send_message(message.chat.id, f'Неверно, осталось попыток: {attempt}')
        bot.register_next_step_handler(message, process_digit_step)
        if attempt == 1:
            bot.send_message(message.chat.id, f'Мдаю... Даю подсказку! Число находится между: {rand - 1} и {rand + 1}')

    else:
        bot.send_message(message.chat.id, f'Вы проиграли! Я загадал число {rand}')
        init_storage(message.chat.id)
        return

@bot.message_handler(func=lambda message: message.text == "Повторюшка")
def repeat(message):
    bot.send_message(message.chat.id, "Сейчас я буду повторять все, что ты скажешь!")
    bot.send_message(message.chat.id, "Если захочешь меня остановить, скажи слово Стоп")
    bot.send_message(message.chat.id, "PS: не присылай стикеры, а то я сломаюсь :D")
    bot.register_next_step_handler(message, repeat_step)

def repeat_step(message):
    if message.text.lower() == 'стоп':
        bot.send_sticker(message.chat.id, open('static/stop.webp', 'rb'))
        return
    else:
        bot.send_message(message.chat.id, message.text)
        bot.register_next_step_handler(message, repeat_step)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        if call.message:
            if call.data == 'good':
                bot.send_message(call.message.chat.id, 'Вот и отличненько')
            elif call.data == 'soso':
                sti = open('static/sticker.webp', 'rb')
                bot.send_sticker(call.message.chat.id, sti)
            elif call.data == 'date':
                bot.send_message(call.message.chat.id, "Сегодня " + str(datetime.datetime.now().date()) + "\nТы тоже в шоке, да?")
            elif call.data == 'time':
                bot.send_message(call.message.chat.id, "Сейчас " + str(datetime.datetime.now().strftime("%H:%M:%S")))

            # remove inline buttons
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Как дела?",
                                  reply_markup=None)
            #show alert

            bot.answer_callback_query(chat_id=call.message.chat.id, show_alert=False,
                                      text = "Это тестовое уведомление")
    except Exception as e:
        print(repr(e))
        #print("ОшибОчка")
#RUN


bot.polling(non_stop=True, interval=0)