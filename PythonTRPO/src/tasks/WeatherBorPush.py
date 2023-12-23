from typing import List, Union, Dict, Any
from apscheduler.schedulers.background import BackgroundScheduler
import telebot
from telebot import types
import requests
import matplotlib.pyplot as plt
import matplotlib
from icecream import ic
from datetime import datetime
import pandas as pd

matplotlib.use("agg")

TELEGRAM_BOT_TOKEN: str = '6803912561:AAHhBAfSSo3hvIeoiZ_nUPlB3hW4bELRlIY'
API_KEY: str = '742c32b186b8d4a4f02f95372d981ed4'

bot: telebot.TeleBot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
scheduler: BackgroundScheduler = BackgroundScheduler()

grad_mng: Union[None, int] = None
city_mng_name: Union[None, str] = None
direction_mng_grad: Union[None, str] = None
current_chat: Union[None, str] = None


def start_monitoring(message: types.Message) -> None:
    """Получаем город для мониторинга"""
    global current_chat
    current_chat = str(message.chat.id)
    bot.send_message(message.chat.id, text="Укажите город для которого хотите установить мониторинг")
    bot.register_next_step_handler(message, grad)


def grad(message: types.Message) -> None:
    """Температуру мониторинга"""
    global city_mng_name
    city_mng_name = message.text
    bot.send_message(message.chat.id, text="Укажите пороговую температуру")
    bot.register_next_step_handler(message, direction_grad)


def direction_grad(message: types.Message) -> None:
    """Направление для уведомления"""
    global grad_mng
    grad_mng = int(message.text)
    keyboard = types.ReplyKeyboardMarkup(row_width=1)
    upper = types.KeyboardButton(text='Выше')
    lower = types.KeyboardButton(text='Ниже')
    keyboard.add(upper, lower)
    bot.send_message(message.chat.id, text="Нажмите на кнопку, чтобы установить направление мониторинга температуры",
                     reply_markup=keyboard)
    bot.register_next_step_handler(message, set_monitoring)


def set_monitoring(message: types.Message) -> None:
    """Сообщение о установке мониторинга"""
    global direction_mng_grad
    direction_mng_grad = message.text.lower()
    bot.send_message(message.chat.id,
                     text=f"Мониторинг погоды установлен для города {city_mng_name} "
                          f"с пороговой температурой {direction_mng_grad} {grad_mng}°C.")
    scheduler.add_job(monitor_weather, 'interval', minutes=10, args=[message])
    scheduler.start()


@bot.message_handler(commands=["start"])
def start(message: types.Message) -> None:
    """Стартовая команда"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    b_geo = types.KeyboardButton(text='🗺️Отправить геолокацию', request_location=True)
    b_mntr = types.KeyboardButton(text='🕵🏻Мониторинг погоды')
    b_forecast = types.KeyboardButton(text='Узнать погоду на 5 дней вперёд')
    markup.add(b_geo, b_mntr, b_forecast)
    bot.send_message(message.chat.id,
                     'Привет! Я бот погоды и вот что я могу: \nВыводить актуальную погоду, просто введите название города или нажмите на кнопку геолокации, устанавливать мониторинг погоды',
                     reply_markup=markup)


@bot.message_handler(content_types=['location'])
def weather_location(message: types.Message) -> None:
    """Считывание геолокации"""
    global lat, lon
    lat, lon = message.location.latitude, message.location.longitude
    city_name = get_city_name_by_coordinates(lat, lon)
    if city_name:
        bot.send_message(message.chat.id, get_weather(city_name))
    else:
        bot.reply_to(message,
                     'Не удалось определить город по геолокации. Пожалуйста, укажите город текстовым сообщением.')


def get_weather(city_name: str) -> str:
    """Получение данных о погоде по названию города"""
    try:
        global data
        url = f'https://api.openweathermap.org/data/2.5/weather?q={city_name}&units=metric&lang=ru&appid={API_KEY}'
        response = requests.get(url)
        data = response.json()
        if response.status_code == 200:
            temperature = data['main']['temp']
            description = data['weather'][0]['description']
            return f'Текущая погода в {city_name}: {temperature}°C, {description}.'
        else:
            return 'Ошибка при получении данных о погоде.'
    except Exception as e:
        print(f'Ошибка: {e}')
        return 'Произошла ошибка. Пожалуйста, попробуйте позже.'


@bot.message_handler(func=lambda message: message.text != '')
def monitor_command(message: types.Message) -> None:
    if message.text == 'Узнать погоду на 5 дней вперёд':
        bot.send_message(message.chat.id, 'Вы выбрали получение прогноза на 5 дней вперёд. Введите название города')
        bot.register_next_step_handler(message, get_forecast)
    elif message.text == '🕵🏻Мониторинг погоды':
        start_monitoring(message)
    else:
        bot.send_message(message.chat.id, get_weather(message.text))


def plot_temperature_graph(data_t: List[Dict[str, Union[str, float]]], city_name: str) -> None:
    """Построение графика температуры на 5 дней"""
    df = pd.DataFrame(data_t)
    df['date'] = pd.to_datetime(df['date'])

    plt.figure(figsize=(10, 6))
    plt.plot(df['date'], df['temperature'], marker='o', linestyle='-', color='b')
    plt.title(f'Температура в городе {city_name} на следующие 5 дней')
    plt.xlabel('Дата')
    plt.ylabel('Температура (°C)')
    plt.grid(True)
    plt.savefig('temperature_graph.png')
    plt.close()


def get_city_name_by_coordinates(latitude: float, longitude: float) -> Union[str, None]:
    """Запрос к API для получения названия города из координат"""
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


def get_forecast(message: types.Message) -> None:
    """Получаем прогноз погоды на 5 дней вперёд"""
    city_name = message.text
    try:
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
            plot_temperature_graph(forecast_data, city_name)
            with open('temperature_graph.png', 'rb') as photo:
                bot.send_photo(message.chat.id, photo)
        else:
            return None
    except Exception as e:
        print(f'Ошибка forecast: {e}')
        return None


def monitor_weather(message: types.Message) -> None:
    """Мониторинг погоды"""
    global grad_mng, city_mng_name, current_chat, direction_mng_grad
    if grad_mng is not None and city_mng_name is not None:
        url = f'https://api.openweathermap.org/data/2.5/weather?q={city_mng_name}&units=metric&lang=ru&appid={API_KEY}'
        response = requests.get(url)
        current_weather = response.json()
        if current_weather is not None:
            temperature = current_weather['main']['temp']

            # Проверяем пороговое значение
            if temperature < grad_mng and direction_mng_grad == "ниже":
                bot.send_message(message.chat.id,
                                 f'Внимание! Температура в {city_mng_name} меньше {grad_mng}°C.')
            elif temperature > grad_mng and direction_mng_grad == "выше":
                bot.send_message(message.chat.id,
                                 f'Внимание! Температура в {city_mng_name} выше {grad_mng}°C.')
        else:
            bot.send_message(message.chat.id,
                             'Не удалось получить данные о погоде. Пожалуйста, попробуйте позже.')


def Bot_Run() -> None:
    bot.polling(none_stop=True, interval=0)
