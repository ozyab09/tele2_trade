import requests
import json

from client import tele2_client


def get_token(default_phone, default_token):
    auth_type = input("Auth trough token [1] or sms [2]: ")

    if auth_type == "1" or auth_type == "":

        phone = input("Your phone number: ")

        if phone == "":
            phone = default_phone
            print("Set default phone:", default_phone)
        token = input("Token: ")

        if token == "":
            token = default_token
            print("Set default token")

    elif auth_type == "2":

        phone = input("Your phone number: ")
        print("Sending sms to your phone..")
        try:
            tele2_client.send_otp(phone)
        except requests.RequestException:
            print('Unable to send sms to your phone')
            exit()

        password = input("Type your sms code: ")
        print('Tying to authenticate code...')
        try:
            token = tele2_client.get_token_from_otp(phone, password)
        except requests.RequestException:
            print('Unable to send sms to your phone')
            exit()
        print('Received token:', token)
        print('Done!')

    return phone, token
