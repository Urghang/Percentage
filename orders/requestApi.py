import concurrent.futures
import requests
import pandas as pd
from bs4 import BeautifulSoup
from zeep import Client
from zeep.transports import Transport


def ordering_micado(QTY, code, comment):
    clientID = '39727'
    password = '39391467'
    urlAPI = 'https://mikado-parts.ru//ws1/basket.asmx/Basket_Add'

    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {
        'ZakazCode': code,
        'QTY': QTY,
        'DeliveryType': '0',
        'Notes': comment,
        'ClientID': clientID,
        'Password': password,
        'ExpressID': '0',
        'StockID': '1'
    }

    try:
        response = requests.post(urlAPI, headers=headers, data=data)
        response.raise_for_status()
        return 'Заказано ' + code + ' ' + QTY
    except requests.exceptions.RequestException as e:
        return 'Ошибка запроса ' + e


def ordering_rosco(code, brand, stock_id, QTY, comment):
    connect = {
        'wsdl': 'http://api.rossko.ru/service/v2.1/GetCheckout',
        'options': {
            'transport': Transport(timeout=1),
        }
    }

    params = {
        'KEY1': 'aae7b144f41c0ef7d840bc948de6dbbc',
        'KEY2': '24e09553d43de0243375642f07efba6d',
        'delivery': {
            'delivery_id': '000000002',
            'address_id': '144623'
        },
        'payment': {
            'payment_id': '1',
            'requisite_id': '29277'
        },
        'contact': {
            'name': 'Aleks',
            'phone': '+74012714217'
        },
        'delivery_parts': True,
        'PARTS': [{
            'Part': {
                'partnumber': code,
                'brand': brand,
                'stock': stock_id,
                'count': QTY,
                'comment': comment
            }
        }]
    }

    client = Client(connect['wsdl'], transport=connect['options']['transport'])

    result = client.service.GetCheckout(**params)

    if result['success']:
        return 'Товар ' + code + ' ' + QTY + ' шт. Успешно заказан.'
    else:
        return result['ItemErrorList']


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
    dict_statuses = {
        0: 'ждёт подтверждения',
        1: 'комплектуется',
        2: 'отгружено',
        3: 'готово к отгрузке',
        5: 'ожидаем поступление',
        6: 'на складе филиала',
        7: 'нет в наличии',
        8: 'отменён клиентом',
        9: 'просрочен',
        31: 'ожидаем товар на складе',
        32: 'возврат на согласовании',
        33: 'товар на экспертизе',
        34: 'возврат отклонён',
        35: 'возврат частично отклонён',
        36: 'товар возвращён'
    }
    all_items = result['OrdersList']['Order']

    for item in all_items:
        parts = item['parts']['part']

        for part in parts:
            code = part['guid']
            quantity = part['count']
            status = dict_statuses[part['status']]
            dict_order[code] = quantity, status

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
                'Stock_id': [],
                'Количество': [],
                'Цена': [],
                'Корзина': [],
                'Статус': []
            }

            basket = get_quantity_in_basket_rosco()

            checkbox = self.checkbox

            part_list = result['PartsList']['Part']

            for part in part_list:
                guid_number = part['guid']
                part_number = part['partnumber']
                brand = part['brand']
                name = part['name']
                stocks = part['stocks']
                crosses = part['crosses']

                if stocks is not None and 'stock' in stocks:
                    stock_list = stocks['stock']

                    for stock_item in stock_list:
                        stock_id = stock_item['id']
                        stock_description = stock_item['description']
                        if checkbox == 'false' and stock_description == 'Партнерский склад':
                            continue
                        else:
                            price = stock_item['price']
                            count = stock_item['count']

                            data['Номер'].append(part_number)
                            data['Поставщик'].append(brand)
                            data['Наименование'].append(name)
                            data['Stock_id'].append(stock_id)
                            data['Склад'].append(stock_description)
                            data['Количество'].append(count)
                            data['Цена'].append(price)
                            basket_tuple = basket.get(guid_number)
                            basket_count = basket_tuple[0] if basket_tuple else ''
                            data['Корзина'].append(basket_count)
                            basket_status = basket_tuple[1] if basket_tuple else ''
                            data['Статус'].append(basket_status)

                if crosses is not None and 'Part' in crosses:
                    cross_parts = crosses['Part']

                    for cross_part in cross_parts:
                        guid_number_cross = cross_part['guid']
                        part_number_cross = cross_part['partnumber']
                        brand_cross = cross_part['brand']
                        name_cross = cross_part['name']
                        stocks_cross = cross_part['stocks']

                        if stocks_cross is not None and 'stock' in stocks_cross:
                            stock_cross_list = stocks_cross['stock']

                            for stock_cross_item in stock_cross_list:
                                stock_id_cross = stock_cross_item['id']
                                stock_description_cross = stock_cross_item['description']
                                if checkbox == 'false' and stock_description_cross == 'Партнерский склад':
                                    continue
                                else:
                                    price_cross = stock_cross_item['price']
                                    count_cross = stock_cross_item['count']

                                    data['Номер'].append(part_number_cross)
                                    data['Поставщик'].append(brand_cross)
                                    data['Наименование'].append(name_cross)
                                    data['Stock_id'].append(stock_id_cross)
                                    data['Склад'].append(stock_description_cross)
                                    data['Количество'].append(count_cross)
                                    data['Цена'].append(price_cross)
                                    basket_cross_tuple = basket.get(guid_number_cross,)
                                    basket_count_cross = basket_cross_tuple[0] if basket_cross_tuple else ''
                                    data['Корзина'].append(basket_count_cross)
                                    basket_status_cross = basket_cross_tuple[1] if basket_cross_tuple else ''
                                    data['Статус'].append(basket_status_cross)

            df = pd.DataFrame(data, columns=['Номер', 'Поставщик', 'Наименование', 'Склад',
                                             'Stock_id', 'Количество', 'Цена', 'Корзина', 'Статус'])

            return 'ROSCO', df
        else:
            df = pd.DataFrame(columns=['Номер', 'Поставщик', 'Наименование', 'Склад',
                                       'Stock_id', 'Количество', 'Цена', 'Корзина', 'Статус'])
            return 'ROSCO', df

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

        return table_names, tables
