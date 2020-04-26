import requests
import json

def getToken(default_phone, defaut_token):

    auth_type = input("Auth trough token [1] or sms [2]: ")

    if auth_type == "1" or auth_type == "":

        phone = input("Your phone number: ")

        if phone == "":
            phone = default_phone
            print("Set default phone:", default_phone)
        token = input("Token: ")

        if token == "":
            token = defaut_token
            print("Set default token")

    elif auth_type == "2":

        phone = input("Your phone number: ")
        data = '{"sender":"Tele2"}'
        r = requests.post("https://msk.tele2.ru/api/validation/number/{}".format(phone), data=data)

        print("Sending sms to your phone..")
        print("Status code: ", r.status_code)

        if r.status_code == 200:

            password = input("Type your sms code: ")
            print('Tying to authenthicate..')
            r = requests.post('https://msk.tele2.ru/auth/realms/tele2-b2c/protocol/openid-connect/token', data={'client_id': 'digital-suite-web-app', 'grant_type': 'password', 'username': phone, 'password': password, 'password_type': 'sms_code'} )

            print('Status code:', r.status_code)
            responde = json.loads(r.text)
            token = responde['access_token']
            print(token)
            print('Done!')
        else:
            print("Error status code")
            exit(0)


    return  phone, token
