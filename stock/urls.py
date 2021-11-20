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
    path('stockToDB1/', stockToDB1, name="db_stockToDB1"),
    path('stockToDB2/', stockToDB2, name="db_stockToDB2"),
    path('stockToDB3/', stockToDB3, name="db_stockToDB3"),
    path('stockToDB4/', stockToDB4, name="db_stockToDB4"),
    path('stockToDB5/', stockToDB5, name="db_stockToDB5"),
    path('stockToDB6/', stockToDB6, name="db_stockToDB6"),
    path('stockToDB7/', stockToDB7, name="db_stockToDB7"),
    path('stockToDB8/', stockToDB8, name="db_stockToDB8"),
    path('stockToDB9/', stockToDB9, name="db_stockToDB9"),
    path('stockToDB10/', stockToDB10, name="db_stockToDB10"),
    path('stockToDB11/', stockToDB11, name="db_stockToDB11"),
    path('stockToDB12/', stockToDB12, name="db_stockToDB12"),
    path('stockToDB13/', stockToDB13, name="db_stockToDB13"),
    path('stockToDB14/', stockToDB14, name="db_stockToDB14"),
    path('stockToDB15/', stockToDB15, name="db_stockToDB15"),
    path('stockToDB16/', stockToDB16, name="db_stockToDB16"),
    path('stockToDB17/', stockToDB17, name="db_stockToDB17"),

    path('companyToDB/', companyToDB, name="db_companyToDB"),
    path('deletStocklist/', deletStocklist, name="deletStocklist"),
    path('kospidataToDB/', kospidataToDB, name="kospidataToDB"),

    # db 삭제하기
    path('deleteStock/<str:name>', deleteStock, name = "deleteStock"),
]
