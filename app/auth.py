import logging


def get_token(default_phone, defaut_token):
    '''
    Возращает телефон и токен
    '''
    phone = default_phone
    # token = input("Token: ")
    token = ''
    if token == "":
        token = defaut_token
        # logging.info("Set default token")

    return phone, token
