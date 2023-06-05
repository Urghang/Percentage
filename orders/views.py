from django.shortcuts import render
from django.http import JsonResponse
from orders.requestApi import DataScraper


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
