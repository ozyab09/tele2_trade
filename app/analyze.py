import requests
import logging
import time
import os
import json

logging.basicConfig(
    level=logging.DEBUG if os.getenv('DEBUG') == 'True' else logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%d-%b-%y %H:%M:%S')


def getRequest(url_postfix, method):

    BASE_URL = 'https://msk.tele2.ru/api/exchange/lots'

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"}

    req = requests.request(
        method,
        f'{BASE_URL}?{url_postfix}',
        headers=headers)

    return req


def main():
    lots = []
    previos_count = 0
    while True:
        try:
            r = getRequest(
                url_postfix='trafficType=voice&volume=50&cost=40&offset=0&limit=50',
                method='get')

            for lot in json.loads(r.text)['data']:
                id = str(lot['id'])
                if id not in lots:
                    lots.append(id)

            current_lots = len(lots)

            if previos_count != current_lots:
                previos_count = current_lots
                logging.info('Current count: {}'.format(str(current_lots)))

        except BaseException:
            logging.info('Тамймаут или еще какая-то хрень')

        time.sleep(1)


if __name__ == '__main__':
    main()
