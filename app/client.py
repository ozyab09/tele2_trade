import requests


class Tele2Client:
    BASE_URL = 'https://msk.tele2.ru'
    AUTH_URL = f'{BASE_URL}/auth'
    API_URL = f'{BASE_URL}/api'
    LOTS_CREATED_URL = BASE_URL + (
        '/https://msk.tele2.ru/api/subscribers/{phone}/exchange/lots/created')

    METHODS = {
        'send-otp': ('post', API_URL + '/validation/number/{phone}'),
        'get-token-from-otp': (
            'post',
            AUTH_URL + '/auth/realms/tele2-b2c/protocol/openid-connect/token'),
        'create-lot': ('put', LOTS_CREATED_URL)
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


tele2_client = Tele2Client()
