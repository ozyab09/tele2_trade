import os

# тиаы лотов
types = {'voice': os.getenv('voice_count') or False,
         'data': os.getenv('data_count') or False,
         'sms': os.getenv('sms_count') or False
         }


# volume - какими пакетами продавать
# multiplier - множитель стоимости
# count - сколько пакетов продавать за раз
price = {'voice':
         {'volume': os.getenv('voice_volume') or 50,
          'multiplier': 0.8,
          'count': os.getenv('voice_count') or 3,
          'params': {'uom': 'min', 'trafficType': 'voice'}
          },
         'data':
             {'volume': os.getenv('data_volume') or 1,
              'multiplier': 15,
              'count': os.getenv('data_count') or 3,
              'params': {'uom': 'gb', 'trafficType': 'data'}
              },
         'sms':
             {'volume': 50,
              'multiplier': 0.5,
              'count': os.getenv('sms_count') or 1,
              'params': {'uom': 'sms', 'trafficType': 'sms'}}
         }

# список emoji
emoji_list = [
    "bomb",
    "cat",
    "cool",
    "devil",
    "rich",
    "scream",
    "tongue",
    "zipped"]

# список для показа имени
show_name_list = ["true", "false"]
