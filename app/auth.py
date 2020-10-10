import logging

def getToken(default_phone, defaut_token):

    phone = default_phone
    token = input("Token: ")

    if token == "":
        token = defaut_token
        logging.info("Set default token")

    return phone, token
