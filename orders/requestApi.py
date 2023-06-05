import concurrent.futures
import requests
import pandas as pd
from bs4 import BeautifulSoup
from zeep import Client
from zeep.transports import Transport


def get_quantity_in_basket_mikado():
    clientID = '39727'
    password = '39391467'
    urlAPI = 'https://mikado-parts.ru/ws1/basket.asmx/Basket_List?'

    url = urlAPI + 'ClientID=' + clientID + '&Password=' + password
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'xml')

    all_items = soup.find_all('BasketItem')
    dict_basket = {}

    for item in all_items:
        zakaz_code = item.find('ZakazCode').text
        quantity = item.find('QTY').text
        dict_basket[zakaz_code] = quantity

    return dict_basket


def get_quantity_in_basket_rosco():
    connect = {
        'wsdl': 'http://api.rossko.ru/service/v2.1/GetOrders',
        'options': {
            'transport': Transport(timeout=1),
        }
    }

    param = {
        'KEY1': 'aae7b144f41c0ef7d840bc948de6dbbc',
        'KEY2': '24e09553d43de0243375642f07efba6d',
        'limit': '100'
    }

    client = Client(connect['wsdl'], transport=connect['options']['transport'])
    result = client.service.GetOrders(**param)

    dict_order = {}
    all_items = result['OrdersList']['Order']

    for item in all_items:
        parts = item['parts']['part']

        for part in parts:
            code = part['guid']
            quantity = part['count']
            dict_order[code] = quantity

    return dict_order


class DataScraper:
    def __init__(self, code, checkbox):
        self.code = code
        self.checkbox = checkbox
        self.parameter_sets = [
            {
                'site': 'mikado'
            },
            {
                'site': 'rosco'
            }
        ]

    def scrape_data_mikado(self):
        clientID = '39727'
        password = '39391467'
        urlAPI = 'https://mikado-parts.ru/ws1/service.asmx/Code_Search?Search_Code='

        url = urlAPI + self.code + '&ClientID=' + clientID + '&Password=' + password + '&FromStockOnly=1'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'xml')

        data = []
        all_items = soup.find_all('Code_List_Row')
        basket = get_quantity_in_basket_mikado()

        for item in all_items:
            current_code = item.find('ZakazCode').text
            supplier = item.find('Supplier').text
            name = item.find('Name').text
            stock_ID = item.find('StokID').text

            if stock_ID == '1':
                stock_name = item.find('StokName').text
                stock_QTY = item.find('StockQTY').text
                price = item.find('PriceRUR').text
                basket_quantity = basket.get(current_code, '')
                data.append([current_code, supplier, name, stock_name, stock_QTY, price, basket_quantity])

        df = pd.DataFrame(data, columns=['Номер', 'Поставщик', 'Наименование',
                                         'Склад', 'Количество', 'Цена', 'Корзина'])

        return 'MIKADO', df

    def scrape_data_rosco(self):
        connect = {
            'wsdl': 'http://api.rossko.ru/service/v2.1/GetSearch',
            'options': {
                'transport': Transport(timeout=1),
            }
        }

        param = {
            'KEY1': 'aae7b144f41c0ef7d840bc948de6dbbc',
            'KEY2': '24e09553d43de0243375642f07efba6d',
            'text': self.code,
            'delivery_id': '000000002',
            'address_id': '144623'
        }

        client = Client(connect['wsdl'], transport=connect['options']['transport'])
        result = client.service.GetSearch(**param)

        if result['success']:
            data = {
                'Номер': [],
                'Поставщик': [],
                'Наименование': [],
                'Склад': [],
                'Количество': [],
                'Цена': [],
                'Корзина': []
            }

            basket = get_quantity_in_basket_rosco()

            checkbox = self.checkbox

            part_list = result['PartsList']['Part']

            for part in part_list:
                guid_number = part['guid']
                part_number = part['partnumber']
                brand = part['brand']
                name = part['name']
                crosses = part['crosses']

                if crosses is not None and 'Part' in crosses:
                    cross_parts = crosses['Part']

                    for cross_part in cross_parts:
                        stock = cross_part['stocks']

                        if stock is not None and 'stock' in stock:
                            stock_list = stock['stock']

                            for stock_item in stock_list:
                                stock_description = stock_item['description']
                                if checkbox == 'false' and stock_description == 'Партнерский склад':
                                    continue
                                else:
                                    price = stock_item['price']
                                    count = stock_item['count']

                                    data['Номер'].append(part_number)
                                    data['Поставщик'].append(brand)
                                    data['Наименование'].append(name)
                                    data['Склад'].append(stock_description)
                                    data['Количество'].append(count)
                                    data['Цена'].append(price)
                                    data['Корзина'].append(basket.get(guid_number, ''))

            df = pd.DataFrame(data, columns=['Номер', 'Поставщик', 'Наименование', 'Склад',
                                             'Количество', 'Цена', 'Корзина'])

            return 'ROSCO', df
        else:
            df = pd.DataFrame(columns=['Номер', 'Поставщик', 'Наименование', 'Склад',
                                       'Количество', 'Цена', 'Корзина'])
            return 'ROSCO', df

    def scrape_data_emex(self):
        pass

    def scrape_data(self):
        tables = []
        table_names = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for params in self.parameter_sets:
                scraper = getattr(self, f"scrape_data_{params['site']}")
                future = executor.submit(scraper)
                futures.append(future)
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                table_names.append(result[0])
                df = result[1]
                tables.append(df)

        # Объедините таблицы и передайте их в шаблон
        # combined_table = pd.concat(tables, axis=1)  # Объединяем таблицы по горизонтали

        return table_names, tables
