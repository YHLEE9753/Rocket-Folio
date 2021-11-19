from django.shortcuts import redirect, render
from django.http import HttpResponse
from collections import OrderedDict
# Include the `fusioncharts.py` file that contains functions to embed the charts.
from RocketFolio.utils import fusion_chart
from stock.models import Stocklist,Stock,Stockhistory
from authentication.models import Account

from . import stock_function

from crypto.models import Crypto

def myPortfolio(request):
    if request.user.is_authenticated:

        # 현재 사용자
        account = Account.objects.get(user = request.user)
        nickname = account.nickname

        # 암호화폐 자산
        crypto_asset = Crypto.objects.filter(account = account).all() # 사용자 암호화페 자산
        print(crypto_asset)
        crypto_name_list = [] #  암호화폐 자산 이름 리스트
        crypto_value_list = [] #  암호화폐 현재 가치 리스트
        crypto_total_value = 0 #  암호화폐 현재 총 가치 
        crypto_total_buy_amount = 0 # 암호화폐 총 투자 금액
        for asset in crypto_asset:
            crypto_name_list.append(asset.name)
            crypto_value_list.append(asset.current_value())
            crypto_total_value += asset.total_value()
            crypto_total_buy_amount += asset.total_buy_amount()


        # 사용자 주식 자산
        stock_data = Stock.objects.filter(account = account)

        price_list = [] # stock 실시간 거래가
        # profit_rate = [] # 수익률
        profit_asset = [] # 실시간 거래가에따른 주식자산
        stock_total_asset = 0 # 주식 총자산금액

        for stock in stock_data:
            checkcode = stock.code

            # 크롤링 함수 import
            price = stock_function.stock_real_price_fun(checkcode)
            price = int(stock_function.deletecomma(str(price)))
            asset = stock.quantity*price
            buy_price = float(stock_function.deletecomma(stock.buy_price))
            profit_rate = round(float((price-(buy_price))/buy_price*100),2)

            # db 추가
            stock.real_price = format(int(price), ',')
            stock.profit_rate = round(profit_rate,2)
            stock.profit_asset = format(int(asset), ',')
            stock.buy_price = format(int(buy_price), ',')
            stock.save()
            
            price_list.append(stock.quantity*buy_price)
            profit_asset.append(asset)

        stock_total_buyprice = sum(price_list) + crypto_total_buy_amount # 암호화폐 추가
        stock_total_asset = sum(profit_asset) + crypto_total_buy_amount # 암호화폐 추가
        subprice = stock_total_asset - stock_total_buyprice
        try:
            stock_total_rate = round(float((stock_total_asset-(stock_total_buyprice))/stock_total_buyprice*100),2)
        except ZeroDivisionError :
            stock_total_rate = 0

        # 비중 저장
        stock_data = Stock.objects.filter(account = account)
        for stock in stock_data:
            profit_asset2 = float(stock_function.deletecomma(stock.profit_asset))*100
            proper = round(profit_asset2/stock_total_asset,2)
            stock.property = proper
            stock.save()

        # 이쁘게 꾸미기
        rateflag = False
        sumflag = False

        if float(stock_total_rate) > 0:
            rateflag = True
        if float(subprice) > 0:
            sumflag = True


        stock_total_buyprice = format(int(stock_total_buyprice), ',')
        stock_total_asset = format(int(stock_total_asset), ',')
        subprice = format(int(subprice), ',')

        if rateflag:
            stock_total_rate = '+'+format(stock_total_rate,',')
        
        if sumflag:
            subprice = '+'+subprice

        

        ########### graph 부분
        names = []
        profitlist = []
        for a in stock_data:
            names.append(str(a.name))
            profitlist.append(float(stock_function.deletecomma(a.profit_asset)))
        names = names + crypto_name_list
        profitlist = profitlist + crypto_value_list
        for name in crypto_name_list:
            names.append(name)
            crypto_asset = Crypto.objects.filter(account = account, name = name).first()
            profitlist.append(crypto_asset.current_value() * crypto_asset.quantity)
        print(names)
        print(profitlist)
        column2D = stock_function.fusion_donut_final(names,profitlist,stock_total_asset)
        
        crypto_asset = Crypto.objects.filter(account = account)
        context = {
                'account' : account,
                'nickname':nickname,
                'subprice':subprice,  # 비트코인합치기
                'stock_data' : stock_data,
                'stock_total_buyprice': stock_total_buyprice, #비트코인 합치기
                'stock_total_asset': stock_total_asset , # 비트코인 합티기
                'stock_total_rate' : stock_total_rate, # 비트코인합티기
                'output' : column2D.render(),
                # 비트코인자산
                'crypto_assets': crypto_asset
                }

        return render(request, "myPortfolio.html",context)
    else:
        return redirect('login')
