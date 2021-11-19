from django.urls import path
from . import views

urlpatterns = [
    path("search_ticker/<str:search_text>/",views.search_ticker,name="search_ticker"),
    path("get_current_price/<str:ticker>/",views.get_current_price),
    path("my_crypto/",views.my_crypto, name="my_crypto"),
    path("search_crypto/",views.search_crypto,name='search_crypto'),
    path("add_crypto_asset/<str:ticker>/",views.add_crypto_asset,name="add_crypto_asset"),
    path('get_total_amount',views.get_total_amount,name="total_amount"),
    path('delete/<int:id>/',views.delete_crypto,name="delete_crypto"),
]