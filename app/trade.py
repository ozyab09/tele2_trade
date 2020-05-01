import auth
import lots
import time
import random
import math
import os

default_phone = os.getenv('default_phone') or ''
default_token = os.getenv('default_token') or ''

data_type = "voice" #voice or data

# список emoji
emoji_list = ["bomb", "cat", "cool","devil", "rich", "scream","tongue", "zipped"]

# настроечные параметры для data и voice
params = {'voice': {'uom': 'min', 'trafficType': 'voice'}, 'data': {'uom': 'gb', 'trafficType': 'data'}}

# какими пакетами продавать // для voice можно вставтить random.randint(6, 9) * 10
price = {'voice': {'volume': 50}, 'data': {'volume': 1}}
# сколько пакетов продавать за раз

count = 7

#получение номера телефона и токена
phone, token = auth.get_token(default_phone, default_token)

print('Trading is trarted')
print('Trade: ', phone)


def main():
    while True:

        #удаление всех лотов
        lots.deleteCurrentLots(phone, token)

        volume = price[data_type]['volume']
        amount = math.ceil(volume * 0.8) if data_type == 'voice' else math.ceil(volume * 15)

        for _ in range(count):
            lots.create_lot(phone, token, amount, volume, emoji_list, params=params[data_type])

        # ожидание
        wait_time = random.randint(180,250)

        print("Waiting {} seconds".format(str(wait_time)))

        time.sleep(wait_time)


if __name__ == '__main__':
    main()
