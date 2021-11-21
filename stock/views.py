from django.http.response import HttpResponse
from RocketFolio.settings import BASE_DIR
from django.shortcuts import redirect, render
from datetime import datetime
from django.utils.dateformat import DateFormat
from django.core import serializers
from django.contrib.messages.context_processors import messages

# 내장함수
import math
import csv
import requests
import os
import pandas as pd

# model 추가
from .models import Stocklist,Stock,Stockhistory,kospi_kosdaq_history
from authentication.models import Account

# 클롤링 함수, fusion chart 생성함수 views.py
from . import stock_function

# fusion graph
from collections import OrderedDict
from .fusioncharts import FusionCharts

def stockToDB(request):
    count = 0
    csv_path = os.path.join(BASE_DIR, 'static','stock','allstockdata')
    for i in range(1,6):
        name = '/dailychart'+str(i)+'.csv'
        f = open(csv_path+name, 'r', encoding='utf-8')
        rdr = csv.reader(f)
        for line in rdr:
            if line[2]=='KOSPI' or line[2] =='KOSDAQ':
                onestock = Stockhistory()
                onestock.code = line[0]
                onestock.name = line[1]
                onestock.section=line[2]
                onestock.date = line[3]
                onestock.open = float(line[4])
                onestock.high = float(line[5])
                onestock.low = float(line[6])
                onestock.close = float(line[7])
                onestock.save()
                count += 1
                print(count)
        f.close() 
    return render(request, "db_stockToDB.html",{"msg":f"{count}개의 Stock을 저장하였습니다"})

def companyToDB(request):
    csv_path = os.path.join(BASE_DIR, 'static','stock')
    # csv_path = os.path.dirname(os.path.abspath(__file__))
    f = open(csv_path + "/stock_name.csv", 'r' ,encoding="utf-8")
    reader = csv.reader(f)
    count = 0
    # KOSPI 200 확인
    k200list = stock_function.KOSPI200()
    for line in reader:
        companyname = line[1]
        code = line[2]
        if companyname in k200list:
            new_stock = Stocklist(company_name=companyname, code=code, KOSPI200 = True)
        else:
            new_stock = Stocklist(company_name=companyname, code=code, KOSPI200 = False)
        new_stock.save()
        count += 1
    return render(request,"db_companyToDB.html",{"msg":f"{count}개의 Voice를 저장하였습니다"})

# 코스피 코스닥 history db 추가
def kospidataToDB(request):
    csv_path = os.path.join(BASE_DIR, 'static','stock','allstockdata')
    # csv_path = os.path.dirname(os.path.abspath(__file__))
    f = open(csv_path + "/kospi_kosdaq.csv", 'r' ,encoding="utf-8")
    reader = csv.reader(f)
    next(reader) #header (첫줄) skip
    count = 0
    # KOSPI 200 확인
    for line in reader:
        section = line[0]
        date = line[1]
        opens = float(line[2])
        high = float(line[3])
        low = float(line[4])
        close = float(line[5])
        new_k = kospi_kosdaq_history(section=section, date=date, open = opens, high = high, low = low, close = close)
        new_k.save()
        count += 1
    return render(request,"kospidataToDB.html",{"msg":f"{count}개의 Voice를 저장하였습니다"})

#####################################################################################
# Stock home 창
def stock_real(request):
    return render(request, 'stock_real.html')


# 자산보여주는 부분
def myStock(request):
    #################################################################
    # 현재 사용자
    account = Account.objects.get(user = request.user)
    nickname = account.nickname
    # 사용자 주식 자산
    stock_data = Stock.objects.filter(account = account)
    ################################################################# 
    # stock_data = Stock.objects.all() # stock 정보############################################################

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

    stock_total_buyprice = sum(price_list)
    stock_total_asset = sum(profit_asset)
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

    column2D = stock_function.fusion_donut_final(names,profitlist,stock_total_asset)
    return render(request, "myStock.html",{'nickname':nickname,'subprice':subprice, 'stock_data' : stock_data,'stock_total_buyprice': stock_total_buyprice, 'stock_total_asset': stock_total_asset , 'stock_total_rate' : stock_total_rate,'output' : column2D.render()})


# 검색부분
def plusStock(request):
    #################################################################
    # 현재 사용자
    account = Account.objects.get(user = request.user)
    
    #################################################################
    if request.method == "POST":
        # 예외처리1
        if request.POST.get('company_name') == '' or request.POST.get('buy_number') == '' or request.POST.get('buy_price') == '':
            return redirect('plusStock')
        # 이미 가지고 있는 종목인경우
        # 사용자 주식 자산
        mystocks = Stock.objects.filter(account = account)
        edit_stock = mystocks.filter(name = request.POST.get('company_name'))

        # 예외처리2
        try:
            number = int(request.POST.get('buy_number'))
            number = int(request.POST.get('buy_price'))
        except ValueError:
            print("숫자가 아님")
            return redirect('plusStock')
        
        # 예외처리3
        if int(request.POST.get('buy_number'))<=0 or int(request.POST.get('buy_price'))<=0:
            return redirect('plusStock')

        # 해당 자산이 없을경우
        if edit_stock.count() == 0:
            new_stock = Stock()
            new_stock.account = account
            new_stock.name = request.POST.get('company_name')
            try:
                new_stock.code = Stocklist.objects.filter(company_name = new_stock.name).first().code
            except AttributeError:
                return redirect('plusStock')
            new_stock.KOSPI200 = Stocklist.objects.filter(company_name = new_stock.name).first().KOSPI200
            new_stock.quantity = request.POST.get('buy_number')
            new_stock.buy_price =request.POST.get('buy_price')
            new_stock.created = datetime.now()
            

            new_stock.real_price = '0'
            new_stock.profit_rate = '0'
            new_stock.profit_asset = '0'
            new_stock.property = '0'
            new_stock.backtesting_past_price = '0'

            new_stock.save()
            print("자산이 새로추가")
        # 해당 자산이 있을경우
        else:
            edit_stock = edit_stock.first()
            print(edit_stock)
            pre_quantity = float(edit_stock.quantity)
            pre_buy_price = float(stock_function.deletecomma(edit_stock.buy_price))
            new_quantity = float(request.POST.get('buy_number'))
            new_buy_price = float(request.POST.get('buy_price'))

            result_quantity = pre_quantity + new_quantity
            result_price = round((((pre_quantity*pre_buy_price)+(new_quantity*new_buy_price))/result_quantity),2)

            edit_stock.quantity = result_quantity
            edit_stock.buy_price = result_price
            edit_stock.created = datetime.now()
            edit_stock.save()
            print("자산이 덮어써짐")
        ################################################################# 
        # edit_stock = Stock.objects.get(name = request.POST.get('company_name'))#######################################
        
        #################################################################
        # 현재 사용자
        # account = Account.objects.get(user = request.user)
        # 사용자 주식 자산
        stock_data = Stock.objects.filter(account = account)
        ################################################################# 
        # stock_data = Stock.objects.all()##########################################
        print(stock_data)
        price_list = []
        for stock in stock_data:
            checkcode = stock.code

            # 크롤링 함수 import
            price = stock_function.stock_real_price_fun(checkcode)

            price_list.append(price)
            
    stock = Stocklist.objects.all()
    return render(request, 'plusStock.html', {'stocklist' : stock})
    

# 주식 상관계수 보여주는 부분
def stock_cor(request):
    # back testing part

    # 전체 자산 불러오기
    #################################################################
    # 현재 사용자
    account = Account.objects.get(user = request.user)
    # 사용자 주식 자산
    stocks = Stock.objects.filter(account = account)
    ################################################################# 
    # stocks = Stock.objects.all()#########################################

    
    # 데이터가 없는 경우 예외처리 발생. 예외처리
    errorcatchnumber =stocks.count()
    if errorcatchnumber == 0:
        # messages.error(request, "Something went wrong")
        return redirect("plusStock")


    names = []
    for stock in stocks:
        names.append(stock.name)

    year = '2017'
    month = '01'
    y_m = year+month

    # 시작년도 월 선택시 년도 월 적용
    if request.method == "POST" and request.POST.get('year')!=None:
        new_year = request.POST.get('year')
        new_month = request.POST.get('month')
        y_m = str(new_year) + str(new_month)

    # 자산 객체별로 보여주기
    min_stock = None
    max_stock = None
    minvalue = 100000
    maxvalue = -100000
    for stock in stocks:
        name = stock.name
        checkcode = Stocklist.objects.get(company_name = name).code
        pastprice = int(Stockhistory.objects.filter(name = name, date = y_m).first().close)
        price = stock_function.stock_real_price_fun(str(checkcode))
        price = stock_function.deletecomma(price)
        stock.profit_rate =  round(float((int(price)-(pastprice))/pastprice*100),2)
        stock.save()
        print("sss")
        print(stock.profit_rate)

        # 최소 최대 수익률 stock 구하기
        if float(stock.profit_rate) < minvalue:
            min_stock = stock
            minvalue = float(stock.profit_rate)
        if float(stock.profit_rate) > maxvalue:
            max_stock = stock
            maxvalue = float(stock.profit_rate)
    #################################################################
    # 현재 사용자
    # account = Account.objects.get(user = request.user)
    # 사용자 주식 자산
    stocks = Stock.objects.filter(account = account)
    ################################################################# 
    # stocks = Stock.objects.all()##################################################3

    today = DateFormat(datetime.now()).format('Ymd')

    all_price = []    
    price_list = [] # stock 실시간 거래가 # 크롤링

    # KOSPI, KOSDAQ 데이터 가져오기
    pastkospi = kospi_kosdaq_history.objects.filter(section = "KOSPI", date = y_m).first().close
    pastkosdaq = kospi_kosdaq_history.objects.filter(section = "KOSDAQ", date = y_m).first().close
    print(pastkospi)
    print(pastkosdaq)
    nowkospikosdaq = stock_function.kospi_kosdaq_function()
    nowkospi = nowkospikosdaq[0]
    nowkodaq = nowkospikosdaq[1]
    changekospi = ''
    for i in nowkospi:
        if i == ',':
            continue
        changekospi += i
    
    changekosdaq = ''
    for i in nowkodaq:
        if i == ',':
            continue
        changekosdaq += i
    kospi_rate = round(float((float(changekospi)-pastkospi)/pastkospi*100),2)
    kosdaq_rate = round(float((float(changekosdaq)-pastkosdaq)/pastkosdaq*100),2)
    kospi_rate = stock_function.ratetochange(kospi_rate)####
    kosdaq_rate = stock_function.ratetochange(kosdaq_rate)####

    # 크롤린 진행
    for name in names:
        stockdata = Stockhistory.objects.filter(name = name)

        # 현재가 크롤링
        checkcode = Stocklist.objects.get(company_name = name).code
        #################################################################
        # 현재 사용자
        # account = Account.objects.get(user = request.user)
        # 사용자 주식 자산
        quan = Stock.objects.filter(account = account).get(code = checkcode).quantity
        ################################################################# 
        # quan = int(Stock.objects.get(code = checkcode).quantity)################################################
        price = stock_function.stock_real_price_fun(checkcode)
        changeprice = ''
        for i in price:
            if i == ',':
                continue
            changeprice += i
        price = int(changeprice)
        price_list.append(price*quan)
        # 크롤링 끝

        result_month = [] # 날짜 저장
        price = [] # 가격 저장
        for stock in stockdata:
            name = stock.name
            if int(stock.date) >= int(y_m):
                # 백테스팅 시작 가격 추가
                if int(stock.date) == int(y_m):
                    mystocks = Stock.objects.filter(account = account, name = name).first()
                    print(stock.close)
                    mystocks.backtesting_past_price = str(format(int(stock.close),','))
                    mystocks.save()

                name = stock.name   
                result_month.append(stock.date) # 날짜 추가
                #################################################################
                # 현재 사용자
                # account = Account.objects.get(user = request.user)
                # 사용자 주식 자산
                stockquantity = int(Stock.objects.filter(account = account).get(name=name).quantity)
                ################################################################# 
                # stockquantity = int(Stock.objects.get(name = name).quantity) # 주식 보유량)################################################
                price.append(stock.close*stockquantity)
        all_price.append(price)
    
    # 처음 시작가 구하기
    start_price = []
    for stock in all_price:
        start_price.append(stock[0])
    start_price = list(map(int,start_price))

    # 백테스팅 마저 진행
    result_price = []
    for i in range(len(all_price[0])):
        sum = 0
        for j in range(len(all_price)):
            sum += all_price[j][i]
        result_price.append(sum)

    # 전체 수익률
    start_sum = 0
    now_sum = 0
    for s,v in zip(start_price,price_list):
        start_sum += s
        now_sum += v
        
    try:
        stock_total_rate = round(float((now_sum-(start_sum))/start_sum*100),2)
    except ZeroDivisionError :
        stock_total_rate = 0

    start_sum = format(int(start_sum), ',')
    now_sum = format(int(now_sum), ',')
    stock_total_rate = stock_function.ratetochange(stock_total_rate)####

    # CAGR = (last_value/first_value)^(1/year_count)-1
    last_value = int(result_price[-1])
    first_value = int(result_price[0])
    year_111 = y_m[0:4]
    year_222 = str(today)[0:4]
    year_count = int(year_222) - int(year_111)
    try:
        CAGR = (math.pow(last_value/first_value, 1/year_count)-1)*100
    except ZeroDivisionError :
        CAGR = stock_total_rate
    CAGR = round(CAGR,2)
    CAGR = stock_function.ratetochange(CAGR)####

    # MDD = (low_value - high_value)/high_vlue * 100
    high_value = int(max(result_price))
    low_value = int(min(result_price))
    MDD = (low_value - high_value)/high_value*100
    MDD = round(MDD,2)
    MDD = stock_function.ratetochange(MDD)####

    # make fusion chart graph
    Line2D = stock_function.fusion_line(result_month, result_price)
    # end backtesting

    # start correlation values
    # 상관계수 select 이름 리스트 생성
    allK = []
    for stock in stocks:
        allK.append(stock.name)

    if request.method == "POST" and request.POST.get('year') == None:
        # corstocklist 에 select 로 받은 주식이름 추가
        max_number = 67 # 2017년부터 2021년까지 데이터개수로 업데이트시 무조건 바뀌는 숫자. 숫자로 놔두는건 굉장히 위험하지만 일단이렇게 둠
        corstocklist = []
        for i in range(1,6):
            optionname = "name"+str(i)
            if request.POST.get(optionname) == 'none':
                continue
            corstocklist.append(request.POST.get(optionname))
        corstocklist = list(set(corstocklist))

        priceDic={}
        sample_price = []
        sample_name = []
        for corstock in corstocklist:
            stockhistorys = Stockhistory.objects.filter(name = corstock)
            pricelist = []
            for st in stockhistorys:
                pricelist.append(st.close)
            if len(pricelist) < max_number:
                max_number = len(pricelist)
            sample_name.append(st.name)
            sample_price.append(pricelist)
        
        # 상장한지 얼마안된 주식의 경우 얼마안된 기간까지만 해서 상관관계 구한다
        for nn, pp in zip(sample_name, sample_price):
            pp = pp[:max_number]
            priceDic[nn]=pp

        All_Price=pd.DataFrame(priceDic)
        corr = All_Price.corr(method = 'pearson')
        print(corr)
        corr = corr.values.tolist()

        # 프론트에 보내기 위해 데이터 처리
        result = []
        for count in range(len(corstocklist)):
            values = []
            values.append(corstocklist[count])
            for count2 in range(len(corr[count])):
                values.append(round(corr[count][count2],2))
            result.append(values)

        y_m = y_m[:4]+'-'+y_m[4:]
        today = today[:4] + '-' + today[4:6]+'-'+today[6:8]
        n_value_year = int(today[:4]) - int(y_m[:4])
        n_value_month =  int(today[4:6]) - int(y_m[4:]) + 12*n_value_year

        return render(request, "stock_cor.html",{'n_year': n_value_year,'n_month':n_value_month,'min_stock' : min_stock, 'max_stock': max_stock,'kospi_rate':kospi_rate,'kosdaq_rate':kosdaq_rate,'allK':allK,'stocklist':corstocklist,'result' : result,'output' : Line2D.render(), 'start_sum' : start_sum, 'now_sum':now_sum, 'stock_total_rate': stock_total_rate ,'today':today, 'start_date' : y_m, 'stocks':stocks,'CAGR':CAGR, 'MDD':MDD})
    
    y_m = y_m[:4]+'-'+y_m[4:]
    today = today[:4] + '-' + today[4:6]+'-'+today[6:8]
    n_value_year =  int(today[:4]) - int(y_m[:4])
    n_value_month =  int(today[4:6]) - int(y_m[4:]) + 12*n_value_year
    return render(request, "stock_cor.html",{'n_year': n_value_year,'n_month':n_value_month,'min_stock' : min_stock, 'max_stock': max_stock,'kospi_rate':kospi_rate,'kosdaq_rate':kosdaq_rate,'allK':allK,'output' : Line2D.render(), 'start_sum' : start_sum, 'now_sum':now_sum, 'stock_total_rate': stock_total_rate,'today':today, 'start_date' : y_m, 'stocks':stocks,'CAGR':CAGR ,'MDD':MDD})

# 개인자산 주식 삭제
def deleteStock(request, name):
    #################################################################
    # 현재 사용자
    account = Account.objects.get(user = request.user)
    # 사용자 주식 자산
    delete_stock = Stock.objects.filter(account = account).get(name = str(name))
    ################################################################# 
    # delete_stock = Stock.objects.get(name = str(name))##########################################
    delete_stock.delete()
    return redirect("myStock")

def deletStocklist(request):
    stock = Stocklist.objects.all()
    for s in stock:
        s.delete()
    
    kos = kospi_kosdaq_history.objects.all()
    for k in kos:
        k.delete()
    return render(request, "deletStocklist.html")


# DB 추가 파트
# dailychart1
def stockToDB1(request):
    csv_path = os.path.join(BASE_DIR, 'static','stock','allstockdata')
    name = '/dailychart1.csv'
    f = open(csv_path+name, 'r', encoding='utf-8')
    data = f.readlines()[:2500]
    count = 0
    for line in data:
        line = line.split(',')
        if line[2]=='KOSPI' or line[2] =='KOSDAQ':
            count +=1
            onestock = Stockhistory()
            onestock.code = line[0]
            onestock.name = line[1]
            onestock.section=line[2]
            onestock.date = line[3]
            onestock.open = float(line[4])
            onestock.high = float(line[5])
            onestock.low = float(line[6])
            onestock.close = float(line[7])
            count+=1
            onestock.save()
        f.close() 
    return render(request, "db_stockToDB.html",{"msg":f"{count}개의 Voice를 저장하였습니다"})

def stockToDB2(request):
    csv_path = os.path.join(BASE_DIR, 'static','stock','allstockdata')
    name = '/dailychart1.csv'
    f = open(csv_path+name, 'r', encoding='utf-8')
    data = f.readlines()[2500:5000]
    count = 0
    for line in data:
        line = line.split(',')
        if line[2]=='KOSPI' or line[2] =='KOSDAQ':
            count +=1
            onestock = Stockhistory()
            onestock.code = line[0]
            onestock.name = line[1]
            onestock.section=line[2]
            onestock.date = line[3]
            onestock.open = float(line[4])
            onestock.high = float(line[5])
            onestock.low = float(line[6])
            onestock.close = float(line[7])
            count+=1
            onestock.save()
        f.close() 
    return render(request, "db_stockToDB.html",{"msg":f"{count}개의 Voice를 저장하였습니다"})

def stockToDB3(request):
    csv_path = os.path.join(BASE_DIR, 'static','stock','allstockdata')
    name = '/dailychart1.csv'
    f = open(csv_path+name, 'r', encoding='utf-8')
    data = f.readlines()[5000:7500]
    count = 0
    for line in data:
        line = line.split(',')
        if line[2]=='KOSPI' or line[2] =='KOSDAQ':
            count +=1
            onestock = Stockhistory()
            onestock.code = line[0]
            onestock.name = line[1]
            onestock.section=line[2]
            onestock.date = line[3]
            onestock.open = float(line[4])
            onestock.high = float(line[5])
            onestock.low = float(line[6])
            onestock.close = float(line[7])
            count+=1
            onestock.save()
        f.close() 
    return render(request, "db_stockToDB.html",{"msg":f"{count}개의 Voice를 저장하였습니다"})

def stockToDB4(request):
    csv_path = os.path.join(BASE_DIR, 'static','stock','allstockdata')
    name = '/dailychart1.csv'
    f = open(csv_path+name, 'r', encoding='utf-8')
    data = f.readlines()[7500:10000]
    count = 0
    for line in data:
        line = line.split(',')
        if line[2]=='KOSPI' or line[2] =='KOSDAQ':
            count +=1
            onestock = Stockhistory()
            onestock.code = line[0]
            onestock.name = line[1]
            onestock.section=line[2]
            onestock.date = line[3]
            onestock.open = float(line[4])
            onestock.high = float(line[5])
            onestock.low = float(line[6])
            onestock.close = float(line[7])
            count+=1
            onestock.save()
        f.close() 
    return render(request, "db_stockToDB.html",{"msg":f"{count}개의 Voice를 저장하였습니다"})

def stockToDB15(request):
    csv_path = os.path.join(BASE_DIR, 'static','stock','allstockdata')
    name = '/dailychart1.csv'
    f = open(csv_path+name, 'r', encoding='utf-8')
    data = f.readlines()[10000:12500]
    count = 0
    for line in data:
        line = line.split(',')
        if line[2]=='KOSPI' or line[2] =='KOSDAQ':
            count +=1
            onestock = Stockhistory()
            onestock.code = line[0]
            onestock.name = line[1]
            onestock.section=line[2]
            onestock.date = line[3]
            onestock.open = float(line[4])
            onestock.high = float(line[5])
            onestock.low = float(line[6])
            onestock.close = float(line[7])
            count+=1
            onestock.save()
        f.close() 
    return render(request, "db_stockToDB.html",{"msg":f"{count}개의 Voice를 저장하였습니다"})

def stockToDB5(request):
    csv_path = os.path.join(BASE_DIR, 'static','stock','allstockdata')
    name = '/dailychart1.csv'
    f = open(csv_path+name, 'r', encoding='utf-8')
    data = f.readlines()[12500:15000]
    count = 0
    for line in data:
        line = line.split(',')
        if line[2]=='KOSPI' or line[2] =='KOSDAQ':
            count +=1
            onestock = Stockhistory()
            onestock.code = line[0]
            onestock.name = line[1]
            onestock.section=line[2]
            onestock.date = line[3]
            onestock.open = float(line[4])
            onestock.high = float(line[5])
            onestock.low = float(line[6])
            onestock.close = float(line[7])
            count+=1
            onestock.save()
        f.close() 
    return render(request, "db_stockToDB.html",{"msg":f"{count}개의 Voice를 저장하였습니다"})

def stockToDB6(request):
    csv_path = os.path.join(BASE_DIR, 'static','stock','allstockdata')
    name = '/dailychart1.csv'
    f = open(csv_path+name, 'r', encoding='utf-8')
    data = f.readlines()[15000:17500]
    count = 0
    for line in data:
        line = line.split(',')
        if line[2]=='KOSPI' or line[2] =='KOSDAQ':
            count +=1
            onestock = Stockhistory()
            onestock.code = line[0]
            onestock.name = line[1]
            onestock.section=line[2]
            onestock.date = line[3]
            onestock.open = float(line[4])
            onestock.high = float(line[5])
            onestock.low = float(line[6])
            onestock.close = float(line[7])
            count+=1
            onestock.save()
        f.close() 
    return render(request, "db_stockToDB.html",{"msg":f"{count}개의 Voice를 저장하였습니다"})

def stockToDB7(request):
    csv_path = os.path.join(BASE_DIR, 'static','stock','allstockdata')
    name = '/dailychart1.csv'
    f = open(csv_path+name, 'r', encoding='utf-8')
    data = f.readlines()[17500:20000]
    count = 0
    for line in data:
        line = line.split(',')
        if line[2]=='KOSPI' or line[2] =='KOSDAQ':
            count +=1
            onestock = Stockhistory()
            onestock.code = line[0]
            onestock.name = line[1]
            onestock.section=line[2]
            onestock.date = line[3]
            onestock.open = float(line[4])
            onestock.high = float(line[5])
            onestock.low = float(line[6])
            onestock.close = float(line[7])
            count+=1
            onestock.save()
        f.close() 
    return render(request, "db_stockToDB.html",{"msg":f"{count}개의 Voice를 저장하였습니다"})

def stockToDB8(request):
    csv_path = os.path.join(BASE_DIR, 'static','stock','allstockdata')
    name = '/dailychart1.csv'
    f = open(csv_path+name, 'r', encoding='utf-8')
    data = f.readlines()[20000:22500]
    count = 0
    for line in data:
        line = line.split(',')
        if line[2]=='KOSPI' or line[2] =='KOSDAQ':
            count +=1
            onestock = Stockhistory()
            onestock.code = line[0]
            onestock.name = line[1]
            onestock.section=line[2]
            onestock.date = line[3]
            onestock.open = float(line[4])
            onestock.high = float(line[5])
            onestock.low = float(line[6])
            onestock.close = float(line[7])
            count+=1
            onestock.save()
        f.close() 
    return render(request, "db_stockToDB.html",{"msg":f"{count}개의 Voice를 저장하였습니다"})

def stockToDB9(request):
    csv_path = os.path.join(BASE_DIR, 'static','stock','allstockdata')
    name = '/dailychart1.csv'
    f = open(csv_path+name, 'r', encoding='utf-8')
    data = f.readlines()[22500:25000]
    count = 0
    for line in data:
        line = line.split(',')
        if line[2]=='KOSPI' or line[2] =='KOSDAQ':
            count +=1
            onestock = Stockhistory()
            onestock.code = line[0]
            onestock.name = line[1]
            onestock.section=line[2]
            onestock.date = line[3]
            onestock.open = float(line[4])
            onestock.high = float(line[5])
            onestock.low = float(line[6])
            onestock.close = float(line[7])
            count+=1
            onestock.save()
        f.close() 
    return render(request, "db_stockToDB.html",{"msg":f"{count}개의 Voice를 저장하였습니다"})

def stockToDB10(request):
    csv_path = os.path.join(BASE_DIR, 'static','stock','allstockdata')
    name = '/dailychart1.csv'
    f = open(csv_path+name, 'r', encoding='utf-8')
    data = f.readlines()[25000:27500]
    count = 0
    for line in data:
        line = line.split(',')
        if line[2]=='KOSPI' or line[2] =='KOSDAQ':
            count +=1
            onestock = Stockhistory()
            onestock.code = line[0]
            onestock.name = line[1]
            onestock.section=line[2]
            onestock.date = line[3]
            onestock.open = float(line[4])
            onestock.high = float(line[5])
            onestock.low = float(line[6])
            onestock.close = float(line[7])
            count+=1
            onestock.save()
        f.close() 
    return render(request, "db_stockToDB.html",{"msg":f"{count}개의 Voice를 저장하였습니다"})

def stockToDB11(request):
    csv_path = os.path.join(BASE_DIR, 'static','stock','allstockdata')
    name = '/dailychart1.csv'
    f = open(csv_path+name, 'r', encoding='utf-8')
    data = f.readlines()[27500:30000]
    count = 0
    for line in data:
        line = line.split(',')
        if line[2]=='KOSPI' or line[2] =='KOSDAQ':
            count +=1
            onestock = Stockhistory()
            onestock.code = line[0]
            onestock.name = line[1]
            onestock.section=line[2]
            onestock.date = line[3]
            onestock.open = float(line[4])
            onestock.high = float(line[5])
            onestock.low = float(line[6])
            onestock.close = float(line[7])
            count+=1
            onestock.save()
        f.close() 
    return render(request, "db_stockToDB.html",{"msg":f"{count}개의 Voice를 저장하였습니다"})

def stockToDB12(request):
    csv_path = os.path.join(BASE_DIR, 'static','stock','allstockdata')
    name = '/dailychart1.csv'
    f = open(csv_path+name, 'r', encoding='utf-8')
    data = f.readlines()[30000:32500]
    count = 0
    for line in data:
        line = line.split(',')
        if line[2]=='KOSPI' or line[2] =='KOSDAQ':
            count +=1
            onestock = Stockhistory()
            onestock.code = line[0]
            onestock.name = line[1]
            onestock.section=line[2]
            onestock.date = line[3]
            onestock.open = float(line[4])
            onestock.high = float(line[5])
            onestock.low = float(line[6])
            onestock.close = float(line[7])
            count+=1
            onestock.save()
        f.close() 
    return render(request, "db_stockToDB.html",{"msg":f"{count}개의 Voice를 저장하였습니다"})

def stockToDB13(request):
    csv_path = os.path.join(BASE_DIR, 'static','stock','allstockdata')
    name = '/dailychart1.csv'
    f = open(csv_path+name, 'r', encoding='utf-8')
    data = f.readlines()[32500:]
    count = 0
    for line in data:
        line = line.split(',')
        if line[2]=='KOSPI' or line[2] =='KOSDAQ':
            count +=1
            onestock = Stockhistory()
            onestock.code = line[0]
            onestock.name = line[1]
            onestock.section=line[2]
            onestock.date = line[3]
            onestock.open = float(line[4])
            onestock.high = float(line[5])
            onestock.low = float(line[6])
            onestock.close = float(line[7])
            count+=1
            onestock.save()
        f.close() 
    return render(request, "db_stockToDB.html",{"msg":f"{count}개의 Voice를 저장하였습니다"})

# dailychart2
def stockToDB14(request):
    csv_path = os.path.join(BASE_DIR, 'static','stock','allstockdata')
    name = '/dailychart2.csv'
    f = open(csv_path+name, 'r', encoding='utf-8')
    data = f.readlines()[:2500]
    count = 0
    for line in data:
        line = line.split(',')
        if line[2]=='KOSPI' or line[2] =='KOSDAQ':
            count +=1
            onestock = Stockhistory()
            onestock.code = line[0]
            onestock.name = line[1]
            onestock.section=line[2]
            onestock.date = line[3]
            onestock.open = float(line[4])
            onestock.high = float(line[5])
            onestock.low = float(line[6])
            onestock.close = float(line[7])
            count+=1
            onestock.save()
        f.close() 
    return render(request, "db_stockToDB.html",{"msg":f"{count}개의 Voice를 저장하였습니다"})

def stockToDB16(request):
    csv_path = os.path.join(BASE_DIR, 'static','stock','allstockdata')
    name = '/dailychart2.csv'
    f = open(csv_path+name, 'r', encoding='utf-8')
    data = f.readlines()[2500:5000]
    count = 0
    for line in data:
        line = line.split(',')
        if line[2]=='KOSPI' or line[2] =='KOSDAQ':
            count +=1
            onestock = Stockhistory()
            onestock.code = line[0]
            onestock.name = line[1]
            onestock.section=line[2]
            onestock.date = line[3]
            onestock.open = float(line[4])
            onestock.high = float(line[5])
            onestock.low = float(line[6])
            onestock.close = float(line[7])
            count+=1
            onestock.save()
        f.close() 
    return render(request, "db_stockToDB.html",{"msg":f"{count}개의 Voice를 저장하였습니다"})

def stockToDB17(request):
    csv_path = os.path.join(BASE_DIR, 'static','stock','allstockdata')
    name = '/dailychart2.csv'
    f = open(csv_path+name, 'r', encoding='utf-8')
    data = f.readlines()[5000:7500]
    count = 0
    for line in data:
        line = line.split(',')
        if line[2]=='KOSPI' or line[2] =='KOSDAQ':
            count +=1
            onestock = Stockhistory()
            onestock.code = line[0]
            onestock.name = line[1]
            onestock.section=line[2]
            onestock.date = line[3]
            onestock.open = float(line[4])
            onestock.high = float(line[5])
            onestock.low = float(line[6])
            onestock.close = float(line[7])
            count+=1
            onestock.save()
        f.close() 
    return render(request, "db_stockToDB.html",{"msg":f"{count}개의 Voice를 저장하였습니다"})

def stockToDB18(request):
    csv_path = os.path.join(BASE_DIR, 'static','stock','allstockdata')
    name = '/dailychart2.csv'
    f = open(csv_path+name, 'r', encoding='utf-8')
    data = f.readlines()[7500:10000]
    count = 0
    for line in data:
        line = line.split(',')
        if line[2]=='KOSPI' or line[2] =='KOSDAQ':
            count +=1
            onestock = Stockhistory()
            onestock.code = line[0]
            onestock.name = line[1]
            onestock.section=line[2]
            onestock.date = line[3]
            onestock.open = float(line[4])
            onestock.high = float(line[5])
            onestock.low = float(line[6])
            onestock.close = float(line[7])
            count+=1
            onestock.save()
        f.close() 
    return render(request, "db_stockToDB.html",{"msg":f"{count}개의 Voice를 저장하였습니다"})

def stockToDB19(request):
    csv_path = os.path.join(BASE_DIR, 'static','stock','allstockdata')
    name = '/dailychart2.csv'
    f = open(csv_path+name, 'r', encoding='utf-8')
    data = f.readlines()[10000:12500]
    count = 0
    for line in data:
        line = line.split(',')
        if line[2]=='KOSPI' or line[2] =='KOSDAQ':
            count +=1
            onestock = Stockhistory()
            onestock.code = line[0]
            onestock.name = line[1]
            onestock.section=line[2]
            onestock.date = line[3]
            onestock.open = float(line[4])
            onestock.high = float(line[5])
            onestock.low = float(line[6])
            onestock.close = float(line[7])
            count+=1
            onestock.save()
        f.close() 
    return render(request, "db_stockToDB.html",{"msg":f"{count}개의 Voice를 저장하였습니다"})

def stockToDB20(request):
    csv_path = os.path.join(BASE_DIR, 'static','stock','allstockdata')
    name = '/dailychart2.csv'
    f = open(csv_path+name, 'r', encoding='utf-8')
    data = f.readlines()[12500:15000]
    count = 0
    for line in data:
        line = line.split(',')
        if line[2]=='KOSPI' or line[2] =='KOSDAQ':
            count +=1
            onestock = Stockhistory()
            onestock.code = line[0]
            onestock.name = line[1]
            onestock.section=line[2]
            onestock.date = line[3]
            onestock.open = float(line[4])
            onestock.high = float(line[5])
            onestock.low = float(line[6])
            onestock.close = float(line[7])
            count+=1
            onestock.save()
        f.close() 
    return render(request, "db_stockToDB.html",{"msg":f"{count}개의 Voice를 저장하였습니다"})

def stockToDB21(request):
    csv_path = os.path.join(BASE_DIR, 'static','stock','allstockdata')
    name = '/dailychart2.csv'
    f = open(csv_path+name, 'r', encoding='utf-8')
    data = f.readlines()[15000:17500]
    count = 0
    for line in data:
        line = line.split(',')
        if line[2]=='KOSPI' or line[2] =='KOSDAQ':
            count +=1
            onestock = Stockhistory()
            onestock.code = line[0]
            onestock.name = line[1]
            onestock.section=line[2]
            onestock.date = line[3]
            onestock.open = float(line[4])
            onestock.high = float(line[5])
            onestock.low = float(line[6])
            onestock.close = float(line[7])
            count+=1
            onestock.save()
        f.close() 
    return render(request, "db_stockToDB.html",{"msg":f"{count}개의 Voice를 저장하였습니다"})

def stockToDB22(request):
    csv_path = os.path.join(BASE_DIR, 'static','stock','allstockdata')
    name = '/dailychart2.csv'
    f = open(csv_path+name, 'r', encoding='utf-8')
    data = f.readlines()[17500:20000]
    count = 0
    for line in data:
        line = line.split(',')
        if line[2]=='KOSPI' or line[2] =='KOSDAQ':
            count +=1
            onestock = Stockhistory()
            onestock.code = line[0]
            onestock.name = line[1]
            onestock.section=line[2]
            onestock.date = line[3]
            onestock.open = float(line[4])
            onestock.high = float(line[5])
            onestock.low = float(line[6])
            onestock.close = float(line[7])
            count+=1
            onestock.save()
        f.close() 
    return render(request, "db_stockToDB.html",{"msg":f"{count}개의 Voice를 저장하였습니다"})

def stockToDB23(request):
    csv_path = os.path.join(BASE_DIR, 'static','stock','allstockdata')
    name = '/dailychart2.csv'
    f = open(csv_path+name, 'r', encoding='utf-8')
    data = f.readlines()[20000:22500]
    count = 0
    for line in data:
        line = line.split(',')
        if line[2]=='KOSPI' or line[2] =='KOSDAQ':
            count +=1
            onestock = Stockhistory()
            onestock.code = line[0]
            onestock.name = line[1]
            onestock.section=line[2]
            onestock.date = line[3]
            onestock.open = float(line[4])
            onestock.high = float(line[5])
            onestock.low = float(line[6])
            onestock.close = float(line[7])
            count+=1
            onestock.save()
        f.close() 
    return render(request, "db_stockToDB.html",{"msg":f"{count}개의 Voice를 저장하였습니다"})

def stockToDB24(request):
    csv_path = os.path.join(BASE_DIR, 'static','stock','allstockdata')
    name = '/dailychart2.csv'
    f = open(csv_path+name, 'r', encoding='utf-8')
    data = f.readlines()[22500:25000]
    count = 0
    for line in data:
        line = line.split(',')
        if line[2]=='KOSPI' or line[2] =='KOSDAQ':
            count +=1
            onestock = Stockhistory()
            onestock.code = line[0]
            onestock.name = line[1]
            onestock.section=line[2]
            onestock.date = line[3]
            onestock.open = float(line[4])
            onestock.high = float(line[5])
            onestock.low = float(line[6])
            onestock.close = float(line[7])
            count+=1
            onestock.save()
        f.close() 
    return render(request, "db_stockToDB.html",{"msg":f"{count}개의 Voice를 저장하였습니다"})

def stockToDB25(request):
    csv_path = os.path.join(BASE_DIR, 'static','stock','allstockdata')
    name = '/dailychart2.csv'
    f = open(csv_path+name, 'r', encoding='utf-8')
    data = f.readlines()[25000:27500]
    count = 0
    for line in data:
        line = line.split(',')
        if line[2]=='KOSPI' or line[2] =='KOSDAQ':
            count +=1
            onestock = Stockhistory()
            onestock.code = line[0]
            onestock.name = line[1]
            onestock.section=line[2]
            onestock.date = line[3]
            onestock.open = float(line[4])
            onestock.high = float(line[5])
            onestock.low = float(line[6])
            onestock.close = float(line[7])
            count+=1
            onestock.save()
        f.close() 
    return render(request, "db_stockToDB.html",{"msg":f"{count}개의 Voice를 저장하였습니다"})

def stockToDB26(request):
    csv_path = os.path.join(BASE_DIR, 'static','stock','allstockdata')
    name = '/dailychart2.csv'
    f = open(csv_path+name, 'r', encoding='utf-8')
    data = f.readlines()[27500:]
    count = 0
    for line in data:
        line = line.split(',')
        if line[2]=='KOSPI' or line[2] =='KOSDAQ':
            count +=1
            onestock = Stockhistory()
            onestock.code = line[0]
            onestock.name = line[1]
            onestock.section=line[2]
            onestock.date = line[3]
            onestock.open = float(line[4])
            onestock.high = float(line[5])
            onestock.low = float(line[6])
            onestock.close = float(line[7])
            count+=1
            onestock.save()
        f.close() 
    return render(request, "db_stockToDB.html",{"msg":f"{count}개의 Voice를 저장하였습니다"})


# dailychart3

def stockToDB27(request):
    csv_path = os.path.join(BASE_DIR, 'static','stock','allstockdata')
    name = '/dailychart3.csv'
    f = open(csv_path+name, 'r', encoding='utf-8')
    data = f.readlines()[:2500]
    count = 0
    for line in data:
        line = line.split(',')
        if line[2]=='KOSPI' or line[2] =='KOSDAQ':
            count +=1
            onestock = Stockhistory()
            onestock.code = line[0]
            onestock.name = line[1]
            onestock.section=line[2]
            onestock.date = line[3]
            onestock.open = float(line[4])
            onestock.high = float(line[5])
            onestock.low = float(line[6])
            onestock.close = float(line[7])
            count+=1
            onestock.save()
        f.close() 
    return render(request, "db_stockToDB.html",{"msg":f"{count}개의 Voice를 저장하였습니다"})

def stockToDB28(request):
    csv_path = os.path.join(BASE_DIR, 'static','stock','allstockdata')
    name = '/dailychart3.csv'
    f = open(csv_path+name, 'r', encoding='utf-8')
    data = f.readlines()[2500:5000]
    count = 0
    for line in data:
        line = line.split(',')
        if line[2]=='KOSPI' or line[2] =='KOSDAQ':
            count +=1
            onestock = Stockhistory()
            onestock.code = line[0]
            onestock.name = line[1]
            onestock.section=line[2]
            onestock.date = line[3]
            onestock.open = float(line[4])
            onestock.high = float(line[5])
            onestock.low = float(line[6])
            onestock.close = float(line[7])
            count+=1
            onestock.save()
        f.close() 
    return render(request, "db_stockToDB.html",{"msg":f"{count}개의 Voice를 저장하였습니다"})

def stockToDB29(request):
    csv_path = os.path.join(BASE_DIR, 'static','stock','allstockdata')
    name = '/dailychart3.csv'
    f = open(csv_path+name, 'r', encoding='utf-8')
    data = f.readlines()[5000:7500]
    count = 0
    for line in data:
        line = line.split(',')
        if line[2]=='KOSPI' or line[2] =='KOSDAQ':
            count +=1
            onestock = Stockhistory()
            onestock.code = line[0]
            onestock.name = line[1]
            onestock.section=line[2]
            onestock.date = line[3]
            onestock.open = float(line[4])
            onestock.high = float(line[5])
            onestock.low = float(line[6])
            onestock.close = float(line[7])
            count+=1
            onestock.save()
        f.close() 
    return render(request, "db_stockToDB.html",{"msg":f"{count}개의 Voice를 저장하였습니다"})

def stockToDB30(request):
    csv_path = os.path.join(BASE_DIR, 'static','stock','allstockdata')
    name = '/dailychart3.csv'
    f = open(csv_path+name, 'r', encoding='utf-8')
    data = f.readlines()[7500:10000]
    count = 0
    for line in data:
        line = line.split(',')
        if line[2]=='KOSPI' or line[2] =='KOSDAQ':
            count +=1
            onestock = Stockhistory()
            onestock.code = line[0]
            onestock.name = line[1]
            onestock.section=line[2]
            onestock.date = line[3]
            onestock.open = float(line[4])
            onestock.high = float(line[5])
            onestock.low = float(line[6])
            onestock.close = float(line[7])
            count+=1
            onestock.save()
        f.close() 
    return render(request, "db_stockToDB.html",{"msg":f"{count}개의 Voice를 저장하였습니다"})

def stockToDB31(request):
    csv_path = os.path.join(BASE_DIR, 'static','stock','allstockdata')
    name = '/dailychart3.csv'
    f = open(csv_path+name, 'r', encoding='utf-8')
    data = f.readlines()[10000:12500]
    count = 0
    for line in data:
        line = line.split(',')
        if line[2]=='KOSPI' or line[2] =='KOSDAQ':
            count +=1
            onestock = Stockhistory()
            onestock.code = line[0]
            onestock.name = line[1]
            onestock.section=line[2]
            onestock.date = line[3]
            onestock.open = float(line[4])
            onestock.high = float(line[5])
            onestock.low = float(line[6])
            onestock.close = float(line[7])
            count+=1
            onestock.save()
        f.close() 
    return render(request, "db_stockToDB.html",{"msg":f"{count}개의 Voice를 저장하였습니다"})

def stockToDB32(request):
    csv_path = os.path.join(BASE_DIR, 'static','stock','allstockdata')
    name = '/dailychart3.csv'
    f = open(csv_path+name, 'r', encoding='utf-8')
    data = f.readlines()[12500:15000]
    count = 0
    for line in data:
        line = line.split(',')
        if line[2]=='KOSPI' or line[2] =='KOSDAQ':
            count +=1
            onestock = Stockhistory()
            onestock.code = line[0]
            onestock.name = line[1]
            onestock.section=line[2]
            onestock.date = line[3]
            onestock.open = float(line[4])
            onestock.high = float(line[5])
            onestock.low = float(line[6])
            onestock.close = float(line[7])
            count+=1
            onestock.save()
        f.close() 
    return render(request, "db_stockToDB.html",{"msg":f"{count}개의 Voice를 저장하였습니다"})

def stockToDB33(request):
    csv_path = os.path.join(BASE_DIR, 'static','stock','allstockdata')
    name = '/dailychart3.csv'
    f = open(csv_path+name, 'r', encoding='utf-8')
    data = f.readlines()[15000:17500]
    count = 0
    for line in data:
        line = line.split(',')
        if line[2]=='KOSPI' or line[2] =='KOSDAQ':
            count +=1
            onestock = Stockhistory()
            onestock.code = line[0]
            onestock.name = line[1]
            onestock.section=line[2]
            onestock.date = line[3]
            onestock.open = float(line[4])
            onestock.high = float(line[5])
            onestock.low = float(line[6])
            onestock.close = float(line[7])
            count+=1
            onestock.save()
        f.close() 
    return render(request, "db_stockToDB.html",{"msg":f"{count}개의 Voice를 저장하였습니다"})

def stockToDB34(request):
    csv_path = os.path.join(BASE_DIR, 'static','stock','allstockdata')
    name = '/dailychart3.csv'
    f = open(csv_path+name, 'r', encoding='utf-8')
    data = f.readlines()[17500:20000]
    count = 0
    for line in data:
        line = line.split(',')
        if line[2]=='KOSPI' or line[2] =='KOSDAQ':
            count +=1
            onestock = Stockhistory()
            onestock.code = line[0]
            onestock.name = line[1]
            onestock.section=line[2]
            onestock.date = line[3]
            onestock.open = float(line[4])
            onestock.high = float(line[5])
            onestock.low = float(line[6])
            onestock.close = float(line[7])
            count+=1
            onestock.save()
        f.close() 
    return render(request, "db_stockToDB.html",{"msg":f"{count}개의 Voice를 저장하였습니다"})

def stockToDB35(request):
    csv_path = os.path.join(BASE_DIR, 'static','stock','allstockdata')
    name = '/dailychart3.csv'
    f = open(csv_path+name, 'r', encoding='utf-8')
    data = f.readlines()[20000:22500]
    count = 0
    for line in data:
        line = line.split(',')
        if line[2]=='KOSPI' or line[2] =='KOSDAQ':
            count +=1
            onestock = Stockhistory()
            onestock.code = line[0]
            onestock.name = line[1]
            onestock.section=line[2]
            onestock.date = line[3]
            onestock.open = float(line[4])
            onestock.high = float(line[5])
            onestock.low = float(line[6])
            onestock.close = float(line[7])
            count+=1
            onestock.save()
        f.close() 
    return render(request, "db_stockToDB.html",{"msg":f"{count}개의 Voice를 저장하였습니다"})

def stockToDB36(request):
    csv_path = os.path.join(BASE_DIR, 'static','stock','allstockdata')
    name = '/dailychart3.csv'
    f = open(csv_path+name, 'r', encoding='utf-8')
    data = f.readlines()[22500:25000]
    count = 0
    for line in data:
        line = line.split(',')
        if line[2]=='KOSPI' or line[2] =='KOSDAQ':
            count +=1
            onestock = Stockhistory()
            onestock.code = line[0]
            onestock.name = line[1]
            onestock.section=line[2]
            onestock.date = line[3]
            onestock.open = float(line[4])
            onestock.high = float(line[5])
            onestock.low = float(line[6])
            onestock.close = float(line[7])
            count+=1
            onestock.save()
        f.close() 
    return render(request, "db_stockToDB.html",{"msg":f"{count}개의 Voice를 저장하였습니다"})

def stockToDB37(request):
    csv_path = os.path.join(BASE_DIR, 'static','stock','allstockdata')
    name = '/dailychart3.csv'
    f = open(csv_path+name, 'r', encoding='utf-8')
    data = f.readlines()[25000:27500]
    count = 0
    for line in data:
        line = line.split(',')
        if line[2]=='KOSPI' or line[2] =='KOSDAQ':
            count +=1
            onestock = Stockhistory()
            onestock.code = line[0]
            onestock.name = line[1]
            onestock.section=line[2]
            onestock.date = line[3]
            onestock.open = float(line[4])
            onestock.high = float(line[5])
            onestock.low = float(line[6])
            onestock.close = float(line[7])
            count+=1
            onestock.save()
        f.close() 
    return render(request, "db_stockToDB.html",{"msg":f"{count}개의 Voice를 저장하였습니다"})

def stockToDB38(request):
    csv_path = os.path.join(BASE_DIR, 'static','stock','allstockdata')
    name = '/dailychart3.csv'
    f = open(csv_path+name, 'r', encoding='utf-8')
    data = f.readlines()[27500:]
    count = 0
    for line in data:
        line = line.split(',')
        if line[2]=='KOSPI' or line[2] =='KOSDAQ':
            count +=1
            onestock = Stockhistory()
            onestock.code = line[0]
            onestock.name = line[1]
            onestock.section=line[2]
            onestock.date = line[3]
            onestock.open = float(line[4])
            onestock.high = float(line[5])
            onestock.low = float(line[6])
            onestock.close = float(line[7])
            count+=1
            onestock.save()
        f.close() 
    return render(request, "db_stockToDB.html",{"msg":f"{count}개의 Voice를 저장하였습니다"})

# dailychart4
def stockToDB39(request):
    csv_path = os.path.join(BASE_DIR, 'static','stock','allstockdata')
    name = '/dailychart4.csv'
    f = open(csv_path+name, 'r', encoding='utf-8')
    data = f.readlines()[:2500]
    count = 0
    for line in data:
        line = line.split(',')
        if line[2]=='KOSPI' or line[2] =='KOSDAQ':
            count +=1
            onestock = Stockhistory()
            onestock.code = line[0]
            onestock.name = line[1]
            onestock.section=line[2]
            onestock.date = line[3]
            onestock.open = float(line[4])
            onestock.high = float(line[5])
            onestock.low = float(line[6])
            onestock.close = float(line[7])
            count+=1
            onestock.save()
        f.close() 
    return render(request, "db_stockToDB.html",{"msg":f"{count}개의 Voice를 저장하였습니다"})

def stockToDB40(request):
    csv_path = os.path.join(BASE_DIR, 'static','stock','allstockdata')
    name = '/dailychart4.csv'
    f = open(csv_path+name, 'r', encoding='utf-8')
    data = f.readlines()[2500:5000]
    count = 0
    for line in data:
        line = line.split(',')
        if line[2]=='KOSPI' or line[2] =='KOSDAQ':
            count +=1
            onestock = Stockhistory()
            onestock.code = line[0]
            onestock.name = line[1]
            onestock.section=line[2]
            onestock.date = line[3]
            onestock.open = float(line[4])
            onestock.high = float(line[5])
            onestock.low = float(line[6])
            onestock.close = float(line[7])
            count+=1
            onestock.save()
        f.close() 
    return render(request, "db_stockToDB.html",{"msg":f"{count}개의 Voice를 저장하였습니다"})

def stockToDB41(request):
    csv_path = os.path.join(BASE_DIR, 'static','stock','allstockdata')
    name = '/dailychart4.csv'
    f = open(csv_path+name, 'r', encoding='utf-8')
    data = f.readlines()[5000:7500]
    count = 0
    for line in data:
        line = line.split(',')
        if line[2]=='KOSPI' or line[2] =='KOSDAQ':
            count +=1
            onestock = Stockhistory()
            onestock.code = line[0]
            onestock.name = line[1]
            onestock.section=line[2]
            onestock.date = line[3]
            onestock.open = float(line[4])
            onestock.high = float(line[5])
            onestock.low = float(line[6])
            onestock.close = float(line[7])
            count+=1
            onestock.save()
        f.close() 
    return render(request, "db_stockToDB.html",{"msg":f"{count}개의 Voice를 저장하였습니다"})

def stockToDB42(request):
    csv_path = os.path.join(BASE_DIR, 'static','stock','allstockdata')
    name = '/dailychart4.csv'
    f = open(csv_path+name, 'r', encoding='utf-8')
    data = f.readlines()[7500:10000]
    count = 0
    for line in data:
        line = line.split(',')
        if line[2]=='KOSPI' or line[2] =='KOSDAQ':
            count +=1
            onestock = Stockhistory()
            onestock.code = line[0]
            onestock.name = line[1]
            onestock.section=line[2]
            onestock.date = line[3]
            onestock.open = float(line[4])
            onestock.high = float(line[5])
            onestock.low = float(line[6])
            onestock.close = float(line[7])
            count+=1
            onestock.save()
        f.close() 
    return render(request, "db_stockToDB.html",{"msg":f"{count}개의 Voice를 저장하였습니다"})

def stockToDB43(request):
    csv_path = os.path.join(BASE_DIR, 'static','stock','allstockdata')
    name = '/dailychart4.csv'
    f = open(csv_path+name, 'r', encoding='utf-8')
    data = f.readlines()[10000:12500]
    count = 0
    for line in data:
        line = line.split(',')
        if line[2]=='KOSPI' or line[2] =='KOSDAQ':
            count +=1
            onestock = Stockhistory()
            onestock.code = line[0]
            onestock.name = line[1]
            onestock.section=line[2]
            onestock.date = line[3]
            onestock.open = float(line[4])
            onestock.high = float(line[5])
            onestock.low = float(line[6])
            onestock.close = float(line[7])
            count+=1
            onestock.save()
        f.close() 
    return render(request, "db_stockToDB.html",{"msg":f"{count}개의 Voice를 저장하였습니다"})

def stockToDB44(request):
    csv_path = os.path.join(BASE_DIR, 'static','stock','allstockdata')
    name = '/dailychart4.csv'
    f = open(csv_path+name, 'r', encoding='utf-8')
    data = f.readlines()[12500:15000]
    count = 0
    for line in data:
        line = line.split(',')
        if line[2]=='KOSPI' or line[2] =='KOSDAQ':
            count +=1
            onestock = Stockhistory()
            onestock.code = line[0]
            onestock.name = line[1]
            onestock.section=line[2]
            onestock.date = line[3]
            onestock.open = float(line[4])
            onestock.high = float(line[5])
            onestock.low = float(line[6])
            onestock.close = float(line[7])
            count+=1
            onestock.save()
        f.close() 
    return render(request, "db_stockToDB.html",{"msg":f"{count}개의 Voice를 저장하였습니다"})

def stockToDB45(request):
    csv_path = os.path.join(BASE_DIR, 'static','stock','allstockdata')
    name = '/dailychart4.csv'
    f = open(csv_path+name, 'r', encoding='utf-8')
    data = f.readlines()[15000:17500]
    count = 0
    for line in data:
        line = line.split(',')
        if line[2]=='KOSPI' or line[2] =='KOSDAQ':
            count +=1
            onestock = Stockhistory()
            onestock.code = line[0]
            onestock.name = line[1]
            onestock.section=line[2]
            onestock.date = line[3]
            onestock.open = float(line[4])
            onestock.high = float(line[5])
            onestock.low = float(line[6])
            onestock.close = float(line[7])
            count+=1
            onestock.save()
        f.close() 
    return render(request, "db_stockToDB.html",{"msg":f"{count}개의 Voice를 저장하였습니다"})

def stockToDB46(request):
    csv_path = os.path.join(BASE_DIR, 'static','stock','allstockdata')
    name = '/dailychart4.csv'
    f = open(csv_path+name, 'r', encoding='utf-8')
    data = f.readlines()[17500:20000]
    count = 0
    for line in data:
        line = line.split(',')
        if line[2]=='KOSPI' or line[2] =='KOSDAQ':
            count +=1
            onestock = Stockhistory()
            onestock.code = line[0]
            onestock.name = line[1]
            onestock.section=line[2]
            onestock.date = line[3]
            onestock.open = float(line[4])
            onestock.high = float(line[5])
            onestock.low = float(line[6])
            onestock.close = float(line[7])
            count+=1
            onestock.save()
        f.close() 
    return render(request, "db_stockToDB.html",{"msg":f"{count}개의 Voice를 저장하였습니다"})

def stockToDB47(request):
    csv_path = os.path.join(BASE_DIR, 'static','stock','allstockdata')
    name = '/dailychart4.csv'
    f = open(csv_path+name, 'r', encoding='utf-8')
    data = f.readlines()[20000:22500]
    count = 0
    for line in data:
        line = line.split(',')
        if line[2]=='KOSPI' or line[2] =='KOSDAQ':
            count +=1
            onestock = Stockhistory()
            onestock.code = line[0]
            onestock.name = line[1]
            onestock.section=line[2]
            onestock.date = line[3]
            onestock.open = float(line[4])
            onestock.high = float(line[5])
            onestock.low = float(line[6])
            onestock.close = float(line[7])
            count+=1
            onestock.save()
        f.close() 
    return render(request, "db_stockToDB.html",{"msg":f"{count}개의 Voice를 저장하였습니다"})

def stockToDB48(request):
    csv_path = os.path.join(BASE_DIR, 'static','stock','allstockdata')
    name = '/dailychart4.csv'
    f = open(csv_path+name, 'r', encoding='utf-8')
    data = f.readlines()[22500:25000]
    count = 0
    for line in data:
        line = line.split(',')
        if line[2]=='KOSPI' or line[2] =='KOSDAQ':
            count +=1
            onestock = Stockhistory()
            onestock.code = line[0]
            onestock.name = line[1]
            onestock.section=line[2]
            onestock.date = line[3]
            onestock.open = float(line[4])
            onestock.high = float(line[5])
            onestock.low = float(line[6])
            onestock.close = float(line[7])
            count+=1
            onestock.save()
        f.close() 
    return render(request, "db_stockToDB.html",{"msg":f"{count}개의 Voice를 저장하였습니다"})

def stockToDB49(request):
    csv_path = os.path.join(BASE_DIR, 'static','stock','allstockdata')
    name = '/dailychart4.csv'
    f = open(csv_path+name, 'r', encoding='utf-8')
    data = f.readlines()[25000:27500]
    count = 0
    for line in data:
        line = line.split(',')
        if line[2]=='KOSPI' or line[2] =='KOSDAQ':
            count +=1
            onestock = Stockhistory()
            onestock.code = line[0]
            onestock.name = line[1]
            onestock.section=line[2]
            onestock.date = line[3]
            onestock.open = float(line[4])
            onestock.high = float(line[5])
            onestock.low = float(line[6])
            onestock.close = float(line[7])
            count+=1
            onestock.save()
        f.close() 
    return render(request, "db_stockToDB.html",{"msg":f"{count}개의 Voice를 저장하였습니다"})

def stockToDB50(request):
    csv_path = os.path.join(BASE_DIR, 'static','stock','allstockdata')
    name = '/dailychart4.csv'
    f = open(csv_path+name, 'r', encoding='utf-8')
    data = f.readlines()[27500:30000]
    count = 0
    for line in data:
        line = line.split(',')
        if line[2]=='KOSPI' or line[2] =='KOSDAQ':
            count +=1
            onestock = Stockhistory()
            onestock.code = line[0]
            onestock.name = line[1]
            onestock.section=line[2]
            onestock.date = line[3]
            onestock.open = float(line[4])
            onestock.high = float(line[5])
            onestock.low = float(line[6])
            onestock.close = float(line[7])
            count+=1
            onestock.save()
        f.close() 
    return render(request, "db_stockToDB.html",{"msg":f"{count}개의 Voice를 저장하였습니다"})

def stockToDB51(request):
    csv_path = os.path.join(BASE_DIR, 'static','stock','allstockdata')
    name = '/dailychart4.csv'
    f = open(csv_path+name, 'r', encoding='utf-8')
    data = f.readlines()[30000:]
    count = 0
    for line in data:
        line = line.split(',')
        if line[2]=='KOSPI' or line[2] =='KOSDAQ':
            count +=1
            onestock = Stockhistory()
            onestock.code = line[0]
            onestock.name = line[1]
            onestock.section=line[2]
            onestock.date = line[3]
            onestock.open = float(line[4])
            onestock.high = float(line[5])
            onestock.low = float(line[6])
            onestock.close = float(line[7])
            count+=1
            onestock.save()
        f.close() 
    return render(request, "db_stockToDB.html",{"msg":f"{count}개의 Voice를 저장하였습니다"})

# dailychart5
def stockToDB52(request):
    csv_path = os.path.join(BASE_DIR, 'static','stock','allstockdata')
    name = '/dailychart5.csv'
    f = open(csv_path+name, 'r', encoding='utf-8')
    data = f.readlines()[:2500]
    count = 0
    for line in data:
        line = line.split(',')
        if line[2]=='KOSPI' or line[2] =='KOSDAQ':
            count +=1
            onestock = Stockhistory()
            onestock.code = line[0]
            onestock.name = line[1]
            onestock.section=line[2]
            onestock.date = line[3]
            onestock.open = float(line[4])
            onestock.high = float(line[5])
            onestock.low = float(line[6])
            onestock.close = float(line[7])
            count+=1
            onestock.save()
        f.close() 
    return render(request, "db_stockToDB.html",{"msg":f"{count}개의 Voice를 저장하였습니다"})

def stockToDB53(request):
    csv_path = os.path.join(BASE_DIR, 'static','stock','allstockdata')
    name = '/dailychart5.csv'
    f = open(csv_path+name, 'r', encoding='utf-8')
    data = f.readlines()[2500:5000]
    count = 0
    for line in data:
        line = line.split(',')
        if line[2]=='KOSPI' or line[2] =='KOSDAQ':
            count +=1
            onestock = Stockhistory()
            onestock.code = line[0]
            onestock.name = line[1]
            onestock.section=line[2]
            onestock.date = line[3]
            onestock.open = float(line[4])
            onestock.high = float(line[5])
            onestock.low = float(line[6])
            onestock.close = float(line[7])
            count+=1
            onestock.save()
        f.close() 
    return render(request, "db_stockToDB.html",{"msg":f"{count}개의 Voice를 저장하였습니다"})

def stockToDB54(request):
    csv_path = os.path.join(BASE_DIR, 'static','stock','allstockdata')
    name = '/dailychart5.csv'
    f = open(csv_path+name, 'r', encoding='utf-8')
    data = f.readlines()[5000:7500]
    count = 0
    for line in data:
        line = line.split(',')
        if line[2]=='KOSPI' or line[2] =='KOSDAQ':
            count +=1
            onestock = Stockhistory()
            onestock.code = line[0]
            onestock.name = line[1]
            onestock.section=line[2]
            onestock.date = line[3]
            onestock.open = float(line[4])
            onestock.high = float(line[5])
            onestock.low = float(line[6])
            onestock.close = float(line[7])
            count+=1
            onestock.save()
        f.close() 
    return render(request, "db_stockToDB.html",{"msg":f"{count}개의 Voice를 저장하였습니다"})

def stockToDB55(request):
    csv_path = os.path.join(BASE_DIR, 'static','stock','allstockdata')
    name = '/dailychart5.csv'
    f = open(csv_path+name, 'r', encoding='utf-8')
    data = f.readlines()[7500:10000]
    count = 0
    for line in data:
        line = line.split(',')
        if line[2]=='KOSPI' or line[2] =='KOSDAQ':
            count +=1
            onestock = Stockhistory()
            onestock.code = line[0]
            onestock.name = line[1]
            onestock.section=line[2]
            onestock.date = line[3]
            onestock.open = float(line[4])
            onestock.high = float(line[5])
            onestock.low = float(line[6])
            onestock.close = float(line[7])
            count+=1
            onestock.save()
        f.close() 
    return render(request, "db_stockToDB.html",{"msg":f"{count}개의 Voice를 저장하였습니다"})

def stockToDB56(request):
    csv_path = os.path.join(BASE_DIR, 'static','stock','allstockdata')
    name = '/dailychart5.csv'
    f = open(csv_path+name, 'r', encoding='utf-8')
    data = f.readlines()[10000:12500]
    count = 0
    for line in data:
        line = line.split(',')
        if line[2]=='KOSPI' or line[2] =='KOSDAQ':
            count +=1
            onestock = Stockhistory()
            onestock.code = line[0]
            onestock.name = line[1]
            onestock.section=line[2]
            onestock.date = line[3]
            onestock.open = float(line[4])
            onestock.high = float(line[5])
            onestock.low = float(line[6])
            onestock.close = float(line[7])
            count+=1
            onestock.save()
        f.close() 
    return render(request, "db_stockToDB.html",{"msg":f"{count}개의 Voice를 저장하였습니다"})

def stockToDB57(request):
    csv_path = os.path.join(BASE_DIR, 'static','stock','allstockdata')
    name = '/dailychart5.csv'
    f = open(csv_path+name, 'r', encoding='utf-8')
    data = f.readlines()[12500:15000]
    count = 0
    for line in data:
        line = line.split(',')
        if line[2]=='KOSPI' or line[2] =='KOSDAQ':
            count +=1
            onestock = Stockhistory()
            onestock.code = line[0]
            onestock.name = line[1]
            onestock.section=line[2]
            onestock.date = line[3]
            onestock.open = float(line[4])
            onestock.high = float(line[5])
            onestock.low = float(line[6])
            onestock.close = float(line[7])
            count+=1
            onestock.save()
        f.close() 
    return render(request, "db_stockToDB.html",{"msg":f"{count}개의 Voice를 저장하였습니다"})

def stockToDB58(request):
    csv_path = os.path.join(BASE_DIR, 'static','stock','allstockdata')
    name = '/dailychart5.csv'
    f = open(csv_path+name, 'r', encoding='utf-8')
    data = f.readlines()[15000:17500]
    count = 0
    for line in data:
        line = line.split(',')
        if line[2]=='KOSPI' or line[2] =='KOSDAQ':
            count +=1
            onestock = Stockhistory()
            onestock.code = line[0]
            onestock.name = line[1]
            onestock.section=line[2]
            onestock.date = line[3]
            onestock.open = float(line[4])
            onestock.high = float(line[5])
            onestock.low = float(line[6])
            onestock.close = float(line[7])
            count+=1
            onestock.save()
        f.close() 
    return render(request, "db_stockToDB.html",{"msg":f"{count}개의 Voice를 저장하였습니다"})

def stockToDB59(request):
    csv_path = os.path.join(BASE_DIR, 'static','stock','allstockdata')
    name = '/dailychart5.csv'
    f = open(csv_path+name, 'r', encoding='utf-8')
    data = f.readlines()[17500:20000]
    count = 0
    for line in data:
        line = line.split(',')
        if line[2]=='KOSPI' or line[2] =='KOSDAQ':
            count +=1
            onestock = Stockhistory()
            onestock.code = line[0]
            onestock.name = line[1]
            onestock.section=line[2]
            onestock.date = line[3]
            onestock.open = float(line[4])
            onestock.high = float(line[5])
            onestock.low = float(line[6])
            onestock.close = float(line[7])
            count+=1
            onestock.save()
        f.close() 
    return render(request, "db_stockToDB.html",{"msg":f"{count}개의 Voice를 저장하였습니다"})

def stockToDB60(request):
    csv_path = os.path.join(BASE_DIR, 'static','stock','allstockdata')
    name = '/dailychart5.csv'
    f = open(csv_path+name, 'r', encoding='utf-8')
    data = f.readlines()[20000:22500]
    count = 0
    for line in data:
        line = line.split(',')
        if line[2]=='KOSPI' or line[2] =='KOSDAQ':
            count +=1
            onestock = Stockhistory()
            onestock.code = line[0]
            onestock.name = line[1]
            onestock.section=line[2]
            onestock.date = line[3]
            onestock.open = float(line[4])
            onestock.high = float(line[5])
            onestock.low = float(line[6])
            onestock.close = float(line[7])
            count+=1
            onestock.save()
        f.close() 
    return render(request, "db_stockToDB.html",{"msg":f"{count}개의 Voice를 저장하였습니다"})

def stockToDB61(request):
    csv_path = os.path.join(BASE_DIR, 'static','stock','allstockdata')
    name = '/dailychart5.csv'
    f = open(csv_path+name, 'r', encoding='utf-8')
    data = f.readlines()[22500:]
    count = 0
    for line in data:
        line = line.split(',')
        if line[2]=='KOSPI' or line[2] =='KOSDAQ':
            count +=1
            onestock = Stockhistory()
            onestock.code = line[0]
            onestock.name = line[1]
            onestock.section=line[2]
            onestock.date = line[3]
            onestock.open = float(line[4])
            onestock.high = float(line[5])
            onestock.low = float(line[6])
            onestock.close = float(line[7])
            count+=1
            onestock.save()
        f.close() 
    return render(request, "db_stockToDB.html",{"msg":f"{count}개의 Voice를 저장하였습니다"})


