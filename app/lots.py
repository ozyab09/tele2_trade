import requests
import json
import time
import random
from datetime import datetime
import logging
import vars


def create_lot(phone, token, amount, volume, params):
    '''
    Создание лота вместе со смайлвми
    '''
    data = {'volume':
            {'value': str(volume),
             'uom': params['uom']},
            'cost':
                {'amount': str(amount),
                 'currency': 'rub'},
            'trafficType': params['trafficType']}

    r = get_request(
        url_postfix='exchange/lots/created',
        phone=phone,
        method='put',
        token=token,
        data=data)

    response = json.loads(r.text)

    if r.status_code != 200:
        logging.warning("Cannot create new {} lot in {}:\n{}\nStatus code: {}".format(
            str(params['trafficType']),
            datetime.now().time(),
            str(response['meta']['message']),
            str(r.status_code)))

        # текущие остатки на маркете
        get_lots(phone, token, is_notify=True)

    time.sleep(1)

    if response['data']:
        id = response['data']['id']
        emoji = [
            random.choice(
                vars.emoji_list), random.choice(
                vars.emoji_list), random.choice(
                vars.emoji_list)]

        data = {'showSellerName': random.choice(vars.show_name_list),
                'emojis': [emoji[0], emoji[1], emoji[2]],
                'cost': {
                    'amount': str(amount),
                    'currency': 'rub'}}
        r = get_request(
            url_postfix=f'exchange/lots/created/{id}',
            phone=phone,
            method='patch',
            token=token,
            data=data)

    return r.status_code


def delete_lot(phone, token, volume, amount, id, uom, trafficType):
    '''
    Удаление лота
    '''
    data = {'volume':
            {'value': str(volume),
             'uom': uom},
            'cost':
                {'amount': str(amount),
                 'currency': 'rub'},
            'trafficType': trafficType}

    logging.debug(
        f'Deleting {trafficType} lot: volume {volume}, amount: {amount}, id: {id}')
    get_request(
        url_postfix=f'exchange/lots/created/{id}',
        phone=phone,
        method='delete',
        token=token,
        data=data)


def get_lots(phone, token, is_notify):
    '''
    Получение списка активных лотов
    '''

    logging.debug('Fetching current lots..')
    r = get_request(
        url_postfix='exchange/lots/created',
        phone=phone,
        method='get',
        token=token)

    if r.status_code == 200:
        created_lot = json.loads(r.text)
    else:
        logging.warning('{0}{1}'.format(r.status_code, r.text))
        created_lot = {}

    current_lots = []

    if created_lot.get('data'):
        for data in created_lot['data']:
            if data['status'] == 'active':
                current_lots.append(
                    {'id': data['id'],
                     'volume': data['volume']['value'],
                     'trafficType': data['trafficType'],
                     'uom': data['volume']['uom'],
                     'amount': data['cost']['amount']})

    if is_notify:
        if len(current_lots) > 0:
            logging.info('Current lots:')
            for lot in current_lots:
                logging.info(
                    f"{lot['trafficType']}: {lot['volume']} {lot['uom']}, {lot['amount']} rub.")
        else:
            logging.info('No created lots')

    return current_lots


def delete_current_lots(phone, token, data_type, current_lots):
    '''
    Удаление текущего лота
    '''
    logging.debug(f'Deleting {data_type} lots')
    if len(current_lots) > 0:
        for lot in current_lots:
            if data_type == lot['trafficType']:
                delete_lot(
                    phone,
                    token,
                    lot['volume'],
                    lot['amount'],
                    lot['id'],
                    lot['uom'],
                    lot['trafficType'])


def get_balance(phone, token):
    '''
    Получение баланса
    '''
    r = get_request(
        url_postfix=f'balance',
        phone=phone,
        method='get',
        token=token)

    if r.status_code == 200:
        balance = json.loads(r.text)['data']['value']
    else:
        logging.info(f'{str(r.status_code)}: {r.text}')
        exit(1)

    return balance


def get_tariff_packages(phone, token):
    '''
    Получение остатков по тарифу
    '''

    r = get_request(
        url_postfix=f'siteMSK/rests',
        phone=phone,
        method='get',
        token=token)
    if r.status_code == 200:
        tariffPackages = json.loads(r.text).get('data').get('tariffPackages')
        logging.info(tariffPackages)


def get_request(url_postfix, method, phone, token, data=None):
    '''
    Функция делает запрос к серверу Tele2 на основе переданных параметров

    :param url_postfix: постфикс, который будет передан в запросе после BASE_URL + phone
    :param method: выполняемый метод запроса (get, post и т.д.)
    :param phone: номер телефона
    :param token: токен
    :param data: передаваемый данные в виде словаря
    :return: вернутся данные request
    '''

    BASE_URL = 'https://msk.tele2.ru/api/subscribers'

    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"}
    payload = data or {}
    req = requests.request(
        method,
        f'{BASE_URL}/{phone}/{url_postfix}',
        headers=headers,
        data=json.dumps(payload))

    return req
