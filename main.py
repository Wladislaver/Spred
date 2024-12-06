import requests
import logging
import schedule
import time
import hmac
import hashlib

# Настройка логирования
logging.basicConfig(filename='bot.log', level=logging.ERROR)

# Функция для получения цен с бирж


def get_bingx_prices():
    try:
        url = 'https://open-api.bingx.com/openApi/swap/v2/quote/price'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and isinstance(data['data'], list):
                return {item['symbol']: float(item['price']) for item in data['data']}
                # print(f'Ответ от BingX: {data}')  # Отладочный вывод
            else:
                logging.error(f'Неожиданный формат ответа от BingX: {data}')
                return {}
        else:
            logging.error(f'Ошибка при получении цен с BingX: статус {
                          response.status_code}')
            return {}
    except Exception as e:
        logging.error(f'Ошибка при получении цен с BingX: {e}')
        return {}


def get_bitget_prices():
    try:
        url = 'https://api.bitget.com/api/v2/spot/market/tickers'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()

            if 'data' in data and isinstance(data['data'], list):
                return {item['symbol']: float(item['lastPr']) for item in data['data']}
                # print(f'Ответ от Bitget: {data}')  # Отладочный вывод
            else:
                logging.error(f'Неожиданный формат ответа от Bitget: {data}')
                return {}
        else:
            logging.error(f'Ошибка при получении цен с Bitget: статус {
                          response.status_code}')
            return {}
    except Exception as e:
        logging.error(f'Ошибка при получении цен с Bitget: {e}')
        return {}


def get_bibit_prices():
    try:
        url = 'https://api.bybit.com/v5/market/tickers'
        params = {'category': 'spot'}
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if 'result' in data and 'list' in data['result']:
                return {item['symbol']: float(item['lastPrice']) for item in data['result']['list']}
                # print(f'Ответ от Bibit: {data}')  # Отладочный вывод
            else:
                logging.error(f'Неожиданный формат ответа от Bybit: {data}')
                return {}
        else:
            logging.error(f'Ошибка при получении цен с Bybit: статус {
                          response.status_code}')
            return {}
    except Exception as e:
        logging.error(f'Ошибка при получении цен с Bybit: {e}')
        return {}


def get_okx_prices():
    try:
        url = 'https://www.okx.com/api/v5/market/tickers'
        params = {'instType': 'SPOT'}
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and isinstance(data['data'], list):
                return {item['instId']: float(item['last']) for item in data['data']}
                # print(f'Ответ от OKX: {data}')  # Отладочный вывод
            else:
                logging.error(f'Неожиданный формат ответа от OKX: {data}')
                return {}
        else:
            logging.error(f'Ошибка при получении цен с OKX: статус {
                          response.status_code}')
            return {}
    except Exception as e:
        logging.error(f'Ошибка при получении цен с OKX: {e}')
        return {}

# Аналогично добавляем функции для остальных бирж


def get_mexc_prices():
    try:
        url = 'https://api.mexc.com/api/v3/ticker/price'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            # print(f'Ответ от MEXC: {data}')  # Отладочный вывод
            return {item['symbol']: float(item['price']) for item in data}
        else:
            logging.error(f'Ошибка при получении цен с MEXC: статус {
                          response.status_code}')
            return {}
    except Exception as e:
        logging.error(f'Ошибка при получении цен с MEXC: {e}')
        return {}


def get_htx_prices():
    try:
        url = 'https://api.htx.com/market/tickers'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and isinstance(data['data'], list):
                return {item['symbol'].upper(): float(item['close']) for item in data['data']}
                # print(f'Ответ от HTX: {data}')  # Отладочный вывод
            else:
                logging.error(f'Неожиданный формат ответа от HTX: {data}')
                return {}
        else:
            logging.error(f'Ошибка при получении цен с HTX: статус {
                          response.status_code}')
            return {}
    except Exception as e:
        logging.error(f'Ошибка при получении цен с HTX: {e}')
        return {}


def get_kucoin_prices():
    try:
        url = 'https://api.kucoin.com/api/v1/market/allTickers'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and 'ticker' in data['data']:
                return {item['symbol'].replace('-', ''): float(item['last']) for item in data['data']['ticker']}
                # print(f'Ответ от ku: {data}')  # Отладочный вывод
            else:
                logging.error(f'Неожиданный формат ответа от KuCoin: {data}')
                return {}
        else:
            logging.error(f'Ошибка при получении цен с KuCoin: статус {
                          response.status_code}')
            return {}
    except Exception as e:
        logging.error(f'Ошибка при получении цен с KuCoin: {e}')
        return {}


# Функция для расчета спреда
def calculate_spread(price1, price2):
    if price1 and price2:
        spread = abs(price1 - price2)
        if spread < 1e-6:  # Исключаем слишком малые спреды
            return None, None

        percentage = (spread / min(price1, price2)) * 100

        return spread, percentage
    else:
        return None, None


# Основная функция, собирающая данные и выводящая спреды
def job():
    all_prices = {}
    all_prices['BingX'] = get_bingx_prices()
    all_prices['Bitget'] = get_bitget_prices()
    all_prices['Bibit'] = get_bibit_prices()
    all_prices['OKX'] = get_okx_prices()
    all_prices['MEXC'] = get_mexc_prices()
    all_prices['HTX'] = get_htx_prices()
    all_prices['KUKOIN'] = get_kucoin_prices()

    spread_results = []

    # Анализируем все пары между биржами
    for exchange1, prices1 in all_prices.items():
        for exchange2, prices2 in all_prices.items():
            if exchange1 != exchange2:
                common_symbols = set(
                    prices1.keys()).intersection(prices2.keys())
                for symbol in common_symbols:
                    spread, percentage = calculate_spread(
                        prices1[symbol], prices2[symbol])
                    if percentage is not None and percentage > 3 and percentage < 15: # здесь регулируем диапазон процентов спреда
                        spread_results.append(
                            (symbol, exchange1, exchange2, spread, percentage))

    # Сортируем результаты по убыванию спреда
    spread_results.sort(key=lambda x: x[4], reverse=True)

    # Выводим результаты
    for result in spread_results:
        symbol, exchange1, exchange2, spread, percentage = result
        message = f'Спред для {symbol} между {exchange1} и {
            exchange2}: {spread} USD ({percentage}%)'
        print(message)


# if __name__ == "__main__":
#     # Проверяем работу функции получения данных с BingX
#     prices = get_kucoin_prices()
#     print(prices)


# Планировщик задач
schedule.every(1).minutes.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
