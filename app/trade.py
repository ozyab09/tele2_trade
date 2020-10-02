import auth
import lots
import time
import random
import math
import os

default_phone = os.getenv('default_phone') or ''
default_token = os.getenv('default_token') or ''

data_type = os.getenv('data_type') or "voice" #voice or data

# список emoji
emoji_list = ["bomb", "cat", "cool","devil", "rich", "scream","tongue", "zipped"]

# список для показа имени
show_name_list = ["true", "false"]
#show_name_list = ["false"]
# настроечные параметры для data и voice
params = {'voice': {'uom': 'min', 'trafficType': 'voice'},
          'data': {'uom': 'gb', 'trafficType': 'data'},
          'sms': {'uom': 'sms', 'trafficType': 'sms'}}

data_volume = os.getenv('data_volume') or 1

# какими пакетами продавать // для voice можно вставтить random.randint(6, 9) * 10
price = {'voice': {'volume': 50},
         'data': {'volume': int(data_volume)},
         'sms': {'volume': 50}}
# сколько пакетов продавать за раз

count = int(os.getenv('count')) or 3

#остановиться когда будет 0
sale_to_zero = os.getenv('sale_to_zero') or False
#получение номера телефона и токена
phone, token = auth.getToken(default_phone, default_token)


print('Trading is strarted')
print('Trade: ', phone)

def main():
    while True:

        #удаление всех лотов
        lots.deleteCurrentLots(phone, token, sale_to_zero)

        volume = price[data_type]['volume']
        if data_type == 'voice':
            amount = math.ceil(volume * 0.8)
        elif data_type == 'sms':
            amount = math.ceil(volume * 0.5)
        else:
            amount = math.ceil(volume * 15)

        for _ in range(count):
            lots.createLot(phone, token, amount, volume, emoji_list, show_name_list, params[data_type])

        # ожидание
        wait_time = random.randint(100,120)

        print("Waiting {} seconds".format(str(wait_time)))

        time.sleep(wait_time)



if __name__ == '__main__':
    main()