import requests
import telebot
from telebot import types
import matplotlib.pyplot as plt
import matplotlib
from icecream import ic
from datetime import datetime
import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler

matplotlib.use('agg')

TELEGRAM_BOT_TOKEN = '6803912561:AAHhBAfSSo3hvIeoiZ_nUPlB3hW4bELRlIY'
API_KEY = '742c32b186b8d4a4f02f95372d981ed4'

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
scheduler = BackgroundScheduler()


# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    b_mntr = types.KeyboardButton(text='🕵🏻Мониторинг погоды')
    b_geo = types.KeyboardButton(text='🗺️Отправить геолокацию', request_location=True)
    markup.add(b_mntr, b_geo)
    bot.send_message(message.chat.id,
                     'Привет! Я бот погоды и вот что я могу: \n1. Прислать состояние погоды на данный момент'
                     '\n2. Составить график погоды на 5 дней вперёд\n3. Установить мониторинг погоды\n Узнать актуальную'
                     ' погоду можно, написав название города или отправив своё местоположение', reply_markup=markup)


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


# @bot.message_handler(text='🕵🏻Мониторинг погоды')
# def monitor_command(message):
#     bot.send_message(message.chat.id,
#                      'Укажи город, а также значение пороговой температуры через пробел\nЯ сообщу, как только температура будет выше или ниже такого значения')
#
#
# def set_monitoring(message, grad, city):
#     global grad_monitor, city_monitor
#     grad_monitor = grad
#     city_monitor = city
#     bot.send_message(chat_id=message.chat.id, text=f'Мониторинг погоды установлен для города {city_monitor} '
#                                                    f'с пороговой температурой {grad_monitor}°C.')


# Регулярная задача для мониторинга погоды каждые 10 минут
# @scheduler.scheduled_job('interval', minutes=10)
# def monitor_weather():
#     global grad_monitor, city_monitor, current_message
#     if grad_monitor is not None and city_monitor is not None:
#         # Ваш код мониторинга погоды
#         current_weather = get_weather(city_monitor)
#
#         if current_weather is not None:
#             temperature = current_weather['main']['temp']
#
#             # Проверяем пороговое значение
#             if temperature < grad_monitor:
#                 bot.send_message(current_message.chat.id, f'Внимание! Температура в {city_monitor} меньше {grad_monitor}°C.')
#             elif temperature > grad_monitor:
#                 bot.send_message(current_message.chat.id, f'Внимание! Температура в {city_monitor} выше {grad_monitor}°C.')
#         else:
#             bot.send_message(current_message.chat.id, 'Не удалось получить данные о погоде. Пожалуйста, попробуйте позже.')


# Обработчик текстовых сообщений
@bot.message_handler(func=lambda message: True)
def weather_text(message):
    global current_message
    current_message = message
    city_name = message.text
    get_weather(city_name)


# Получение данных о погоде от OpenWeatherMap API
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


# Получение исторических данных о погоде от API
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


# Строим график температуры за последние 5 дней
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


# Получение названия города по координатам с использованием геокодера
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


# Запуск планировщика
scheduler.start()

# Запуск бота
if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)
