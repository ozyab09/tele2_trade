import requests
import json
import time

from client import tele2_client


def create_lot(phone, token, amount, volume, emoji_list, params):
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
    tele2_client.add_emoji(phone=phone, token=token, id=id, amount=amount, emoji_list=emoji_list)


def delete_lot(phone, token, volume, amount, id, uom, traffic_type):

    print(
        'Deleting lot id: volume {}, amount: {}, id: {}'.format(volume, amount,
                                                                id), end='  ')

    status = tele2_client.delete_lot(phone=phone, token=token, id=id, volume=volume,
                            uom=uom, amount=amount,
                            traffic_type=traffic_type)
    time.sleep(1)

    print(status)

def get_lots(phone, token):

    print('Fetching current lots..')

    try:
        created_lots = tele2_client.get_lots(phone=phone, token=token)
    except requests.RequestException:
        print("Cannot fetch lots")
        exit(0)

    current_lots = []

    for data in created_lots['data']:
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
