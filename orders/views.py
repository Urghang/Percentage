from django.shortcuts import render
from django.http import JsonResponse
from orders.requestApi import DataScraper, ordering_micado, ordering_rosco


def index(request):
    return render(request, 'index.html')


def process_data(request):
    if request.method == 'POST':
        input_data = request.POST.get('inputData', '')
        checkbox_value = request.POST.get('myCheckbox', '')
        scarper = DataScraper(code=input_data, checkbox=checkbox_value)
        table_names, tables = scarper.scrape_data()
        result_jsons = [df.to_json(orient='records', force_ascii=False) for df in tables]
        return JsonResponse({'table_names': table_names,
                             'tables': result_jsons})

    return JsonResponse({'error': 'Invalid request method'})


def new_order(request):
    if request.method == 'POST':
        table_name = request.POST.get('tablename', '')
        qty_data = request.POST.get('qty', '')
        part_id = request.POST.get('partId', '')
        stock_id = request.POST.get('stock_id', '')
        postavshik_id = request.POST.get('postavshik_id', '')
        comment = request.POST.get('comment', '')

        if table_name == "MIKADO":
            result = ordering_micado(qty_data, part_id, comment)

            return JsonResponse({'result': result})
        elif table_name == "ROSCO":
            result = ordering_rosco(part_id, postavshik_id, stock_id, qty_data, comment)
            return JsonResponse({'result': result})
