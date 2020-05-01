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

    # add name and emojis
    lot_id = lot['id']
    emojis = random.choices(emoji_list, k=3)
    try:
        tele2_client.patch_lot(
            phone=phone, token=token, lot_id=lot_id,
            show_name_list=show_name_list,
            emojis=emojis, amount=amount)
    except requests.RequestException:
        print('Unable to update the lot')
        exit()


def delete_lot(phone, token, volume, amount, lot_id, uom, traffic_type):
    print(f'Deleting lot id: volume {volume}, amount: {amount}, id: {lot_id}',
          end='  ')
    try:
        tele2_client.delete_lot(
            phone=phone, token=token, lot_id=lot_id, volume=volume, uom=uom,
            amount=amount, traffic_type=traffic_type)
    except requests.RequestException:
        print('Unable to delete the lot')
        exit()

    time.sleep(1)


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
