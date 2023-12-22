import telebot
from telebot import types
import requests
import matplotlib.pyplot as plt
import matplotlib
from icecream import ic
from datetime import datetime
import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler

matplotlib.use("agg")

TELEGRAM_BOT_TOKEN = '6803912561:AAHhBAfSSo3hvIeoiZ_nUPlB3hW4bELRlIY'
API_KEY = '742c32b186b8d4a4f02f95372d981ed4'

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
scheduler = BackgroundScheduler()


def start_monitoring(message):
    bot.send_message(message.chat.id, text="Укажите город для которого хотите установить мониторинг")
    bot.register_next_step_handler(message, grad)


def grad(message):
    global city_mng_name
    city_mng_name = message.text
    bot.send_message(message.chat.id, text="Укажите пороговую температуру")
    bot.register_next_step_handler(message, direction_grad)


def direction_grad(message):
    global grad_mng
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    upper = types.InlineKeyboardButton(text='Выше')
    lower = types.InlineKeyboardButton(text='Ниже')
    keyboard.add(upper, lower)
    bot.send_message(message.chat.id, text="Нажмите на кнопку, чтобы установить направление мониторинга температуры",
                     reply_markup=keyboard)
    bot.register_next_step_handler(message, set_monitoring)


def set_monitoring(message):
    global direction_mng_grad
    if message.text == 'Выше':
        direction_mng_grad = 1
    elif message.text == "Ниже":
        direction_mng_grad = 0
    bot.send_message(message.chat.id, text=f"Мониторинг погоды установлен для города {city_mng_name} "
                                           f"с пороговой температурой {grad_mng}°C.")
    scheduler.start()


# Обработчик команды /strart
@bot.message_handler(commands=["start"])
def start(message):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    b_mntr = types.InlineKeyboardButton(text='🕵🏻Мониторинг погоды', callback_data='button_monitoring')
    b_geo = types.InlineKeyboardButton(text='🗺️Отправить геолокацию', request_location=True, callback_data='geo')
    b_forecast = types.InlineKeyboardButton(text='График на 5 дней', callback_data='forecast')
    keyboard.add(b_geo, b_forecast, b_mntr)
    bot.send_message(message.chat.id,
                     'Привет! Я бот погоды и вот что я могу: \n1. Прислать состояние погоды на данный момент'
                     '\n2. Составить график погоды на 5 дней вперёд\n3. Установить мониторинг погоды\n Узнать актуальную'
                     ' погоду можно, написав название города или отправив своё местоположение', reply_markup=keyboard)


# Обработчик геолокации
@bot.message_handler(content_types=['location'])
def weather_location(message):
    global lat, lon
    lat, lon = message.location.latitude, message.location.longitude
    city_name = get_city_name_by_coordinates(lat, lon)

    if city_name:
        get_weather(city_name)
    else:
        bot.reply_to(message,
                     'Не удалось определить город по геолокации. Пожалуйста, укажите город текстовым сообщением.')


def get_weather(city_name):
    try:
        global data
        url = f'https://api.openweathermap.org/data/2.5/weather?q={city_name}&units=metric&lang=ru&appid={API_KEY}'
        ic(url)
        response = requests.get(url)
        data = response.json()

        ic(data)
        if response.status_code == 200:
            temperature = data['main']['temp']
            description = data['weather'][0]['description']
            return f'Текущая погода в {city_name}: {temperature}°C, {description}.'
        else:
            return 'Ошибка при получении данных о погоде.'
    except Exception as e:
        print(f'Ошибка: {e}')
        return 'Произошла ошибка. Пожалуйста, попробуйте позже.'


@bot.callback_query_handler(func=lambda call: True)
def monitor_command(call):
    if call.data == 'button_monitoring':
        bot.send_message(call.message.chat.id, 'Вы выбрали мониторинг погоды')
        start_monitoring(call.message)

    elif call.data == 'forecast':
        get_forecast()
        pass
    elif call.data == 'geo':
        weather_location(call.message)


def plot_temperature_graph(data_t, city_name):
    df = pd.DataFrame(data_t)
    df['date'] = pd.to_datetime(df['date'])

    plt.figure(figsize=(10, 6))
    plt.plot(df['date'], df['temperature'], marker='o', linestyle='-', color='b')
    plt.title(f'Температура в городе {city_name} на следующие 5 дней')
    plt.xlabel('Дата')
    plt.ylabel('Температура (°C)')
    plt.grid(True)
    plt.savefig('temperature_graph.png')


def get_city_name_by_coordinates(latitude, longitude):
    try:
        url = f'http://nominatim.openstreetmap.org/reverse?format=json&lat={latitude}&lon={longitude}'
        response = requests.get(url)
        data_t = response.json()

        if response.status_code == 200 and 'address' in data_t:
            city = data_t['address'].get('city') or data_t['address'].get('town') or data_t['address'].get('village')
            return city
        else:
            return None
    except Exception as e:
        print(f'Ошибка: {e}')
        return None


def get_forecast(city_name):
    try:
        ic('forecast')
        url = f'http://api.openweathermap.org/data/2.5/forecast?q={city_name}&appid={API_KEY}&units=metric&lang=ru'
        response = requests.get(url)
        data_t = response.json()

        if response.status_code == 200:
            forecast_data = []

            for item in data_t['list']:
                timestamp = item['dt']
                date = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                temperature = item['main']['temp']
                forecast_data.append({'date': date, 'temperature': temperature})

            return forecast_data
        else:
            return None
    except Exception as e:
        print(f'Ошибка forecast: {e}')
        return None


@bot.message_handler(func=lambda message: True)
def any_message(message):
    city_name = message.text
    get_weather(city_name)


@scheduler.scheduled_job('interval', minutes=10)
def monitor_weather():
    global grad_monitor, city_monitor, current_message
    if grad_monitor is not None and city_monitor is not None:
        # Ваш код мониторинга погоды
        url = f'https://api.openweathermap.org/data/2.5/weather?q={city_monitor}&units=metric&lang=ru&appid={API_KEY}'
        ic(url)
        response = requests.get(url)
        current_weather = response.json()

        if current_weather is not None:
            temperature = current_weather['main']['temp']

            # Проверяем пороговое значение
            if temperature < grad_monitor:
                bot.send_message(current_message.chat.id,
                                 f'Внимание! Температура в {city_monitor} меньше {grad_monitor}°C.')
            elif temperature > grad_monitor:
                bot.send_message(current_message.chat.id,
                                 f'Внимание! Температура в {city_monitor} выше {grad_monitor}°C.')
        else:
            bot.send_message(current_message.chat.id,
                             'Не удалось получить данные о погоде. Пожалуйста, попробуйте позже.')


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)
