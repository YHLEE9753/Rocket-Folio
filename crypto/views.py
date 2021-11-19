from django.shortcuts import redirect, render
from .models import Crypto, CryptoTicker
from authentication.models import Account
from django.http import JsonResponse
from RocketFolio.utils import fusion_chart
import pyupbit

# search_text를 입력받아 코인 이름 첫번째 글자부터 찾아 리턴  
# search_text: "리" -> 리스크, 리플, 리퍼리움
def search_ticker(request,search_text):
    all_ticker = CryptoTicker.objects.all()

    rtn_ticker = []
    search_length = len(search_text)
    if search_text[0] == '비':
        for ticker in all_ticker:
            if ticker.name == "비트코인":
                rtn_ticker.append([ticker.ticker,ticker.name,ticker.market,format(ticker.current_value(),',')])
    else:
        for ticker in all_ticker:
            if search_text == ticker.name[:search_length]:
                rtn_ticker.append([ticker.ticker,ticker.name,ticker.market,format(ticker.current_value(),',')])
    return JsonResponse({"tickers":rtn_ticker})

    # all_ticker = CryptoTicker.objects.all()
    # rtn_ticker = []
    # search_length = len(search_text)
    # for ticker in all_ticker:
    #     if search_text == ticker.name[:search_length]:
    #         rtn_ticker.append([ticker.ticker,ticker.name,ticker.market,format(ticker.current_value(),',')])
    # print(rtn_ticker)
    # return JsonResponse({"tickers":rtn_ticker})

# ticker를 받아서 최신 가격을 리턴
def get_current_price(request, ticker):
    current_price = pyupbit.get_current_price(f"KRW-{ticker}")
    return JsonResponse({'current_price':current_price})

# 암호화폐 자산 추가 페이지
def search_crypto(request):
    return render(request,'search_crypto.html')

# crypto 자산 추가
def add_crypto_asset(request, ticker):
    search_result = CryptoTicker.objects.get(ticker = ticker)
    print(search_result)
    if request.method == "POST":
        quantity = request.POST.get('quantity')
        price = request.POST.get('price')
        account = Account.objects.get(user=request.user)
        new_crypto = Crypto()
        new_crypto.account = account
        new_crypto.name = search_result.name
        new_crypto.ticker = search_result.ticker
        new_crypto.market = search_result.market
        new_crypto.quantity = quantity
        new_crypto.buy_price = price
        new_crypto.save()
        return redirect('my_crypto')
    return render(request,"add_crypto.html",{"crypto_ticker":search_result})

# crypto 자산 상세페이지
def my_crypto(request):
    # 현재 로그인한 계정
    account = Account.objects.get(user = request.user)
    print(account.nickname)
    crypto_list = Crypto.objects.filter(account = account).all()
    print(crypto_list)
    if len(crypto_list) == 0:
        return render(request,'my_crypto.html',{"account":account})
    else:
        total_value = 0
        total_buy_amount = 0
        total_quantity = 0
        crypto_name_list = []
        crypto_value_list = []
        for crypto in crypto_list:
            crypto_name_list.append(crypto.name)
            crypto_value_list.append(crypto.current_value())
            total_value += crypto.total_value()
            total_buy_amount += crypto.total_buy_amount()
            total_quantity += crypto.quantity
        print(f"crypto_name_list : {crypto_name_list}")
        print(f"crypto_value_list : {crypto_value_list}")
        crypto_yield = round(float((total_value-(total_buy_amount))/total_buy_amount*100),2)
        column2D = fusion_chart.fusion_donut(crypto_name_list, crypto_value_list,format(round(total_value,2),',')) 
        context = {"account":account,
                    "crypto_list": crypto_list,
                    "total_value": total_value,
                    "total_buy_amount":total_buy_amount,
                    "subprice":total_value-total_buy_amount,
                    "crypto_yield":crypto_yield,
                    "total_quantity":total_quantity,
                    "output":column2D.render()}
        return render(request,'my_crypto.html',context)

def get_total_amount(request):
    account = Account.objects.get(user = request.user)
    crypto_list = Crypto.objects.filter(account = account).all()
    if len(crypto_list) == 0:
        return JsonResponse({"total_amount":0})
    else:
        total_amount = 0
        for crypto in crypto_list:
            total_amount += crypto.total_value()
        return JsonResponse({"total_amount":total_amount})

def delete_crypto(request, id):
    target_crypto = Crypto.objects.get(id=id)
    target_crypto.delete()
    return redirect('my_crypto')

