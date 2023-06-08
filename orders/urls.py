from django.urls import path
from . import views


urlpatterns = [
    path('', views.index),
    path('process_data/', views.process_data, name='process_data'),
    path('new_order/', views.new_order, name='new_order'),
]
