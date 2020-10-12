import logging

def getToken(default_phone, defaut_token):
    '''
    Возращает телефон и токен
    '''
    phone = default_phone
    token = input("Token: ")

    if token == "":
        token = defaut_token
        logging.info("Set default token")

    return phone, token
