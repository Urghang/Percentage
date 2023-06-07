import ssl

import requests
import pandas as pd
import urllib3 as urllib3
from bs4 import BeautifulSoup
from zeep import Client
from zeep.transports import Transport

code = 'lf-2179'
brand = 'Zekkert'
stock = 'HST228'
count = '1'

connect = {
    'wsdl': 'http://api.rossko.ru/service/v2.1/GetCheckout',
    'options': {
        'transport': Transport(timeout=1),
    }
}

param = {
    'KEY1': 'aae7b144f41c0ef7d840bc948de6dbbc',
    'KEY2': '24e09553d43de0243375642f07efba6d',
    'delivery': {
        'delivery_id': '000000002',
        'address_id': '144623'
    },
    'payment': {'payment_id': '1',
                'requisite_id': ''
                },
    'contact': {
        'name': 'Олег',
        'phone': '+74012710517'
    },
    'delivery_parts': True,
    'PARTS': {
        'Part':
            {
                'partnumber': code,
                'brand': brand,
                'stock': stock,
                'count': '1'
            }
        }
}

client = Client(connect['wsdl'], transport=connect['options']['transport'])
try:
    result = client.service.GetCheckout(**param)
    print(result)
except Exception as e:
    print('Ошибка', e)

# connect = {
#             'wsdl': 'http://api.rossko.ru/service/v2.1/GetCheckoutDetails',
#             'options': {
#                 'transport': Transport(timeout=1),
#             }
#         }
#
# param = {
#             'KEY1': 'aae7b144f41c0ef7d840bc948de6dbbc',
#             'KEY2': '24e09553d43de0243375642f07efba6d',
#
#         }
#
# client = Client(connect['wsdl'], transport=connect['options']['transport'])
# result = client.service.GetCheckoutDetails(**param)
# print(result)
