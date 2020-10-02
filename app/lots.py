import requests
import json
import time
import random
from  datetime import datetime

def createLot(phone, token, amount, volume, emoji_list, show_name_list, params):

    headers = {"Authorization": "Bearer {}".format(token)}
    data = {'volume': {'value': str(volume), 'uom': params['uom']}, 'cost':{'amount': str(amount), 'currency': 'rub'}, 'trafficType': params['trafficType']}

    print('Creating new lot: volume {}, amount {}'.format(volume, amount), end ='   ')

    r = requests.put("https://msk.tele2.ru/api/subscribers/{}/exchange/lots/created".format(phone), headers=headers, data=json.dumps(data))

    print(r.status_code, end=" ")

    response = json.loads(r.text)

    if r.status_code != 200:
        print(f"\nCannot create new lot in {datetime.now().time()}:\n{response['meta']['message']}")
        exit(0)

    time.sleep(1)

    id = response['data']['id']
    emoji = [random.choice(emoji_list), random.choice(emoji_list), random.choice(emoji_list)]

    #add name and emoji
    data = {'showSellerName': random.choice(show_name_list), 'emojis': [emoji[0],emoji[1], emoji[2]],'cost':{'amount':str(amount), 'currency': 'rub'}}

    print(' '.join(s for s in emoji))

    r = requests.patch("https://msk.tele2.ru/api/subscribers/{}/exchange/lots/created/{}".format(phone, id), headers=headers, data=json.dumps(data))


def deleteLot(phone, token, volume, amount, id, uom, trafficType):

    headers = {"Authorization": "Bearer {}".format(token)}
    data = {'volume': {'value': str(volume), 'uom': uom}, 'cost': {'amount': str(amount), 'currency': 'rub'},
            'trafficType': trafficType}

    print('Deleting lot id: volume {}, amount: {}, id: {}'.format(volume, amount, id), end ='  ')

    r = requests.delete("https://msk.tele2.ru/api/subscribers/{}/exchange/lots/created/{}".format(phone, id), headers=headers,
                     data=json.dumps(data))

    response = json.loads(r.text)

    time.sleep(1)

    print(str(r.status_code), response['meta']['status'])


def getLots(phone, token):

    headers = {"Authorization": "Bearer {}".format(token)}

    print('Fetching current lots..')

    r = requests.get("https://msk.tele2.ru/api/subscribers/{}/exchange/lots/created".format(phone), headers=headers)

    if r.status_code == 200:
        created_lot = json.loads(r.text)
    else:
        print(r.status_code, r.text)
        exit(0)

    current_lots = []

    for data in created_lot['data']:
        if data['status'] == 'active':
            current_lots.append({'id': data['id'], 'volume': data['volume']['value'], 'trafficType': data['trafficType'], 'uom': data['volume']['uom'], 'amount': data['cost']['amount']})

    return current_lots

def deleteCurrentLots(phone, token, sale_to_zero):

    current_lots = getLots(phone, token)

    print('Found {} lot(s)'.format(str(len(current_lots))))

    if sale_to_zero and len(current_lots) == 0:
        print(f'sale_to_zero is {sale_to_zero} and len(current_lots)={len(current_lots)}, stopping')
        exit(0)

    if len(current_lots) > 0:
        for lot in current_lots:
            deleteLot(phone, token, lot['volume'], lot['amount'], lot['id'], lot['uom'], lot['trafficType'])
