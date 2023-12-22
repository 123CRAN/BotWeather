import requests
import telebot
import matplotlib.pyplot as plt
import matplotlib
from datetime import datetime
from icecream import ic
import pandas as pd

matplotlib.use('agg')

TELEGRAM_BOT_TOKEN = '6803912561:AAHhBAfSSo3hvIeoiZ_nUPlB3hW4bELRlIY'
OPENWEATHERMAP_API_KEY = '742c32b186b8d4a4f02f95372d981ed4'

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)


# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, 'Привет! Я бот погоды. Отправь мне геолокацию или укажи город текстом, используя /w '
                          '*Город*.')


# Обработчик команды /weather
@bot.message_handler(commands=['weather'])
def weather_command(message):
    city_name = ' '.join(message.text.split()[1:])
    if not city_name:
        bot.reply_to(message, 'Пожалуйста, укажите город после команды /weather.')
        return

    process_weather_request(message, city_name)


# Обработчик геолокации
@bot.message_handler(content_types=['location'])
def weather_location(message):
    global lat, lon
    lat, lon = message.location.latitude, message.location.longitude
    city_name = get_city_name_by_coordinates(lat, lon)

    if city_name:
        process_weather_request(message, city_name)
    else:
        bot.reply_to(message,
                     'Не удалось определить город по геолокации. Пожалуйста, укажите город текстовым сообщением.')


# Обработчик текстовых сообщений
@bot.message_handler(func=lambda message: True)
def weather_text(message):
    city_name = message.text
    if city_name and not city_name.startswith('/'):
        process_weather_request(message, city_name)


# Обработка запроса погоды
def process_weather_request(message, city_name):
    # Получаем текущую погоду
    ic(city_name)
    current_weather = get_weather(city_name)

    # Получаем исторические данные о погоде за последние 5 дней
    historical_weather = get_forecast(city_name)

    # Строим график
    if historical_weather is not None:
        plot_temperature_graph(historical_weather, city_name)

        # Отправляем текущую погоду
        bot.send_message(message.chat.id, current_weather)

        # Отправляем график
        bot.send_photo(message.chat.id, photo=open('temperature_graph.png', 'rb'))
    else:
        bot.reply_to(message, 'Не удалось получить данные о погоде. Пожалуйста, попробуйте позже.')


# Получение данных о погоде от OpenWeatherMap API
def get_weather(city_name):
    try:
        global data
        url = f'https://api.openweathermap.org/data/2.5/weather?q={city_name}&units=metric&lang=ru&appid={OPENWEATHERMAP_API_KEY}'
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
        url = f'http://api.openweathermap.org/data/2.5/forecast?q={city_name}&appid={OPENWEATHERMAP_API_KEY}&units=metric&lang=ru'
        response = requests.get(url)
        data = response.json()

        if response.status_code == 200:
            forecast_data = []

            for item in data['list']:
                timestamp = item['dt']
                date = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                temperature = item['main']['temp']
                forecast_data.append({'date': date, 'temperature': temperature})

            return forecast_data
        else:
            return None
    except Exception as e:
        print(f'Ошибка: {e}')
        return None

# Строим график температуры за последние 5 дней
def plot_temperature_graph(data, city_name):
    df = pd.DataFrame(data)
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
        data = response.json()

        if response.status_code == 200 and 'address' in data:
            city = data['address'].get('city') or data['address'].get('town') or data['address'].get('village')
            return city
        else:
            return None
    except Exception as e:
        print(f'Ошибка: {e}')
        return None


if __name__ == '__main__':
    while True:
        # в бесконечном цикле постоянно опрашиваем бота — есть ли новые сообщения
        try:
            bot.polling(none_stop=True, interval=0)
        # если возникла ошибка — сообщаем про исключение и продолжаем работу
        except Exception as e:
            ic(f'❌❌❌❌❌ Сработало исключение! ❌❌❌❌❌ \n Ошибка - {e}')
