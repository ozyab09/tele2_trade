import requests
import random

class Tele2Client:

    BASE_URL = 'https://msk.tele2.ru'
    AUTH_URL = f'{BASE_URL}/auth'
    API_URL = f'{BASE_URL}/api/'
    LOTS_CREATED_URL = API_URL + (
        'subscribers/{phone}/exchange/lots/created')
    DELETE_LOT_URL = API_URL + (
        'subscribers/{phone}/exchange/lots/created/{id}')
    ADD_EMOJI_URL = API_URL + (
        'subscribers/{phone}/exchange/lots/created/{id}')



    METHODS = {
        'send-otp': ('post', API_URL + '/validation/number/{phone}'),
        'get-token-from-otp': (
            'post',
            AUTH_URL + '/auth/realms/tele2-b2c/protocol/openid-connect/token'),
        'create-lot': ('put', LOTS_CREATED_URL),
        'get-lots': ('get', LOTS_CREATED_URL),
        'add-emoji': ('patch', ADD_EMOJI_URL),
        'delete-lot': ('delete', DELETE_LOT_URL)
    }

    def _call(self, method_name, token=None, url_args=None, payload=None):
        url_args = url_args or {}
        http_method, url_template = self.METHODS[method_name]
        url = url_template.format(**url_args)
        headers = {}
        if token:
            headers.update({'Authorization': f'Bearer {token}'})

        response = requests.request(http_method, url, json=payload,
                                    headers=headers)
        try:
            response.raise_for_status()
        except requests.RequestException:
            print('Error condition', response.status_code, response.text)
        return response.json()

    def send_otp(self, phone):
        return self._call('send-otp', url_args={
            'phone': phone
        }, payload={
            "sender": "Tele2"
        })

    def get_token_from_otp(self, phone, otp):
        return self._call('get-token-from-otp', payload={
            'client_id': 'digital-suite-web-app',
            'grant_type': 'password', 'username': phone,
            'password': otp, 'password_type': 'sms_code'
        })['access_token']

    def create_lot(self, phone, token, volume, uom, amount, traffic_type):
        data = {'volume': {'value': str(volume), 'uom': uom,
                           'cost': {'amount': str(amount), 'currency': 'rub'},
                           'trafficType': traffic_type}}
        return self._call('create-lot', token=token, url_args={'phone': phone},
                          payload=data)

    def delete_lot(self, phone, token, id, volume, uom, amount, traffic_type):
        data = {'volume': {'value': str(volume), 'uom': uom},
                'cost': {'amount': str(amount), 'currency': 'rub'},
                'trafficType': traffic_type}

        return self._call('delete-lot', token=token, url_args={'phone': phone, 'id': id},
                          payload=data)

    def add_emoji(self, phone, token, id, amount, emoji_list):

        # список для показа имени
        show_name_list = ["true", "false"]

        emoji = [random.choice(emoji_list), random.choice(emoji_list),
                 random.choice(emoji_list)]

        data = {'showSellerName': random.choice(show_name_list),
                'emojis': [emoji[0], emoji[1], emoji[2]],
                'cost': {'amount': str(amount), 'currency': 'rub'}}

        return self._call('create-lot', token=token, url_args={'phone': phone},
                          payload=data)

    def get_lots(self, phone, token):
        return self._call('get-lots', token=token, url_args={'phone': phone})


tele2_client = Tele2Client()
