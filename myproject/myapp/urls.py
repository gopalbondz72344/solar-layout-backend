# solar/urls.py
from django.urls import path
from . import views 
urlpatterns = [
    path('layout-register/', views.layout_Register, name='layout_register'),
    path('solar-plants/', views.get_all_plants, name="get-solar-plants"),
    path('get-details/<str:plant_id>/',views.get_details_by_plant_id, name='get_details_by_plant_id'),
    # path('get-power-output/<str:plant_id>/', views.get_power_output, name='get_power_output'),

]
