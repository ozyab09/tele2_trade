import requests
import json
import time
import random
from datetime import datetime
import logging
import vars

def createLot(phone, token, amount, volume, params):

    data = {'volume':
                {'value': str(volume),
                 'uom': params['uom']},
            'cost':
                {'amount': str(amount),
                 'currency': 'rub'},
            'trafficType': params['trafficType']}

    r = getRequest(url_postfix='exchange/lots/created', phone=phone, method='put', token=token, data=data)

    response = json.loads(r.text)

    if r.status_code != 200:
        logging.warning("Cannot create new {} lot in {}:\n{}\nStatus code: {}".format(
            str(params['trafficType']),
            datetime.now().time(),
            str(response['meta']['message']),
            str(r.status_code)))

    time.sleep(1)

    if response['data']:
        id = response['data']['id']
        emoji = [random.choice(vars.emoji_list), random.choice(vars.emoji_list), random.choice(vars.emoji_list)]

        data = {'showSellerName': random.choice(vars.show_name_list),
                'emojis': [emoji[0],emoji[1], emoji[2]],
                'cost':{
                    'amount':str(amount),
                    'currency': 'rub'}}
        r = getRequest(url_postfix=f'exchange/lots/created/{id}', phone=phone, method='patch', token=token, data=data)

    return r.status_code

def deleteLot(phone, token, volume, amount, id, uom, trafficType):

    data = {'volume':
                {'value': str(volume),
                 'uom': uom},
            'cost':
                {'amount': str(amount),
                 'currency': 'rub'},
            'trafficType': trafficType}

    logging.debug(f'Deleting {trafficType} lot: volume {volume}, amount: {amount}, id: {id}')
    getRequest(url_postfix=f'exchange/lots/created/{id}', phone=phone, method='delete', token=token, data=data)

def getLots(phone, token):

    logging.debug('Fetching current lots..')
    r = getRequest(url_postfix='exchange/lots/created', phone=phone, method='get', token=token)

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

    return current_lots

def deleteCurrentLots(phone, token, data_type, current_lots):

    if len(current_lots) > 0:
        for lot in current_lots:
            if data_type == lot['trafficType']:
                deleteLot(phone, token, lot['volume'], lot['amount'], lot['id'], lot['uom'], lot['trafficType'])


def getBalance (phone, token):

    r = getRequest(url_postfix=f'balance', phone=phone, method='get', token=token)

    if r.status_code == 200:
        balance = json.loads(r.text)['data']['value']
    else:
        balance = 0

    return balance

def getRequest(url_postfix, method, phone, token, data=None):

    BASE_URL = 'https://msk.tele2.ru/api/subscribers'

    headers = {"Authorization": f"Bearer {token}", "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"}

    if data:
        req = requests.request(method, f'{BASE_URL}/{phone}/{url_postfix}', headers=headers, data=json.dumps(data))
    else:
        req = requests.request(method, f'{BASE_URL}/{phone}/{url_postfix}', headers=headers)

    return req
