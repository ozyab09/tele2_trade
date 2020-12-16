import auth
import lots
import time
import random
import math
import os
import logging
import vars

logging.basicConfig(
    level=logging.DEBUG if os.getenv('DEBUG') == 'True' else logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%d-%b-%y %H:%M:%S')

default_phone = os.getenv('default_phone') or exit(1)
default_token = os.getenv('default_token') or ''

# получение номера телефона и токена
phone, token = auth.get_token(default_phone, default_token)


def main():
    start_balance = previous_balance = lots.get_balance(phone, token)
    logging.info(
        'Trading is strarted. Current balance: {}'.format(
            str(start_balance)))
    lots.get_tariff_packages(phone, token)

    while True:

        current_balance = lots.get_balance(phone, token)
        if current_balance != previous_balance:
            logging.warning('Current balance: {}, start balance: {}, different: {}'.format(
                str(current_balance), str(start_balance), current_balance - start_balance))
            lots.get_tariff_packages(phone, token)

        # for history
        previous_balance = current_balance

        logging.debug('Updating current lots')

        if vars.types['voice'] or vars.types['data'] or vars.types['sms']:

            current_lots = lots.get_lots(phone, token, is_notify=False)

            for data_type in vars.types:
                if vars.types[data_type]:

                    volume = int(vars.price[data_type]['volume'])
                    multiplier = vars.price[data_type]['multiplier']
                    amount = math.ceil(volume * multiplier)
                    count = int(vars.price[data_type]['count'])

                    lots.delete_current_lots(phone,
                                             token,
                                             data_type,
                                             current_lots)

                    for i in range(count):
                        status = lots.create_lot(
                            phone, token, amount, volume, vars.price[data_type]['params'])
                        if status != 200:
                            vars.types.update({data_type: False})
                            logging.info(
                                f'Error when try to create new {data_type} lot. Try #{str(i)}')
                            break

                    wait_time = random.randint(80, 120)

            logging.debug(f"Waiting {str(wait_time)} seconds")

            time.sleep(wait_time)
        else:
            logging.info("Finished")
            exit(0)


if __name__ == '__main__':
    main()
