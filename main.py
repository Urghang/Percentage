import requests
import pandas as pd
from bs4 import BeautifulSoup
from zeep import Client
from zeep.transports import Transport

connect = {
            'wsdl': 'http://api.rossko.ru/service/v2.1/GetOrders',
            'options': {
                'transport': Transport(timeout=1),
            }
        }

param = {
            'KEY1': 'aae7b144f41c0ef7d840bc948de6dbbc',
            'KEY2': '24e09553d43de0243375642f07efba6d',
            'limit': '50'
        }

client = Client(connect['wsdl'], transport=connect['options']['transport'])
result = client.service.GetOrders(**param)

dict_order = {}
all_items = result['OrdersList']['Order']

for item in all_items:
    parts = item['parts']['part']

    for part in parts:
        code = part['partnumber']
        quantity = part['count']
        dict_order[code] = quantity

print(dict_order)
