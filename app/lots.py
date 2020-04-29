import requests
import json
import time
import random

from client import tele2_client


def create_lot(phone, token, amount, volume, emoji_list, show_name_list,
               params):
    print('Creating new voice lot: volume {}, amount {}'.format(volume, amount),
          end='   ')
    try:
        lot = tele2_client.create_lot(phone=phone, token=token, volume=volume,
                                      uom=params['uom'], amount=amount,
                                      traffic_type=params['trafficType'])
    except requests.RequestException:
        print("Cannot create new lot")
        exit(0)

    time.sleep(1)

    id = lot['data']['id']
    emoji = [random.choice(emoji_list), random.choice(emoji_list),
             random.choice(emoji_list)]

    # add name and emoji
    data = {'showSellerName': random.choice(show_name_list),
            'emojis': [emoji[0], emoji[1], emoji[2]],
            'cost': {'amount': str(amount), 'currency': 'rub'}}

    print(' '.join(s for s in emoji))

    r = requests.patch("https://msk.tele2.ru/api/subscribers/{}/exchange/lots/created/{}".format(phone, id), headers=headers, data=json.dumps(data))


def delete_lot(phone, token, volume, amount, id, uom, trafficType):
    headers = {"Authorization": "Bearer {}".format(token)}
    data = {'volume': {'value': str(volume), 'uom': uom},
            'cost': {'amount': str(amount), 'currency': 'rub'},
            'trafficType': trafficType}

    print(
        'Deleting lot id: volume {}, amount: {}, id: {}'.format(volume, amount,
                                                                id), end='  ')

    r = requests.delete(
        "https://msk.tele2.ru/api/subscribers/{}/exchange/lots/created/{}".format(
            phone, id), headers=headers,
        data=json.dumps(data))

    response = json.loads(r.text)

    time.sleep(1)

    print(str(r.status_code), response['meta']['status'])


def get_lots(phone, token):
    headers = {"Authorization": "Bearer {}".format(token)}

    print('Fetching current lots..')

    r = requests.get(
        "https://msk.tele2.ru/api/subscribers/{}/exchange/lots/created".format(
            phone), headers=headers)

    if r.status_code == 200:
        created_lot = json.loads(r.text)
    else:
        print(r.status_code)
        exit(0)

    current_lots = []

    for data in created_lot['data']:
        if data['status'] == 'active':
            current_lots.append({'id': data['id'], 'volume': data['volume']['value'], 'trafficType': data['trafficType'], 'uom': data['volume']['uom'], 'amount': data['cost']['amount']})

    return current_lots

def deleteCurrentLots(phone, token):
    current_lots = get_lots(phone, token)

    print('Found {} lot(s)'.format(str(len(current_lots))))

    if len(current_lots) > 0:
        for lot in current_lots:
            delete_lot(phone, token, lot['volume'], lot['amount'], lot['id'],
                       lot['uom'], lot['trafficType'])
