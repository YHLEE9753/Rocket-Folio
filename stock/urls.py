from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', stock_real, name = 'stock_real'),
    path('mystock/', myStock, name = "myStock"),
    path('plusstock/', plusStock, name = "plusStock"),
    path('stock_cor/', stock_cor, name = "stock_cor"),

    # logout
    path('logout/', auth_views.LogoutView.as_view(), name = "logout"),

    # db 추가하기
    path('stockToDB/', stockToDB, name="db_stockToDB"),
    path('companyToDB/', companyToDB, name="db_companyToDB"),
    path('deletStocklist/', deletStocklist, name="deletStocklist"),
    path('kospidataToDB/', kospidataToDB, name="kospidataToDB"),

    # db 삭제하기
    path('deleteStock/<str:name>', deleteStock, name = "deleteStock"),
]
