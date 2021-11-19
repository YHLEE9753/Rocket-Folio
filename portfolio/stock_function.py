from bs4 import BeautifulSoup
import requests
import re
from collections import OrderedDict
from .fusioncharts import FusionCharts

# 콤마 제거 함수
def deletecomma(text)->str:
    changetext = ''
    for i in text:
        if i == ',':
            continue
        changetext += i
    return changetext

# +, - 붙여주기
def ratetochange(text:str)->str:
    textflag = False
    text = float(text)
    if text>0:
        textflag = True
    
    if textflag:
        return '+'+str(text)
    else:
        return str(text)

# 주식 실시간 크롤링 함수
def stock_real_price_fun(checkcode) -> int:
    real_price = 'notfound'
    while(len(checkcode)!=6):
        checkcode = '0' + checkcode
    url = 'https://finance.naver.com/item/main.nhn?code=' + checkcode
    response = requests.get(url)
    response.raise_for_status()
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    today = soup.select_one('#chart_area > div.rate_info > div')
    real_price = today.select_one('.blind')  
    real_price = real_price.get_text()
    
    return real_price

# KOSPI 200 크롤링 함수
def KOSPI200() -> list:
    BaseUrl = 'http://finance.naver.com/sise/entryJongmok.nhn?&page='
    names = []
    codes = []
    result = []
    for i in range(1, 21):
        url = BaseUrl + str(i)
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'lxml')
        items = soup.find_all('td', {'class': 'ctg'})
        for item in items:
            #print(item)
            txt = item.a.get('href') # https://finance.naver.com/item/main.nhn?code=006390
            k = re.search('[\d]+', txt) ##정규표현식 사용. [\d] 숫자표현, + : 반복
            if k:
                code = k.group()
                name = item.text
                data = code, name
                result.append(data)
                names.append(name)
                codes.append(code)
    return names

# fusion chart - Donut
def fusion_donut(stock_data, sum_data):
    colorcode = ['#3C42D6','#5359FF','#7479FF','#8B8FFF','#9B9FFF','#BBD3FC','#DEEAFF','#ECF3FF','#FFFFFF']


    dataSource = OrderedDict()

    chartConfig = OrderedDict()
    chartConfig["chartBottomMargin"] = "100"
    chartConfig["bgColor"] = "#F5F9FF"
    chartConfig["showpercentvalues"] = "1"
    chartConfig["legendPosition"] = "right"
    chartConfig["legendCaption"] = "종목별 비중"
    chartConfig["legendCaptionBold"] = "1"
    chartConfig["legendCaptionFont"] = "Source Han Sans K"
    chartConfig["legendCaptionFontSize"] = "28"
    chartConfig["legendCaptionFontColor"] = "#4A536A"
    chartConfig["legendIconScale"] = "2"
    chartConfig["legendItemFontBold"] = "100"
    chartConfig["legendItemFont"] = "Source Han Sans K"
    chartConfig["legendItemFontColor"] = "#000000"
    chartConfig["legendItemFontSize"] = "20"
    chartConfig["defaultcenterlabel"] = str(sum_data)
    chartConfig["centerLabelFontSize"] = "24"
    chartConfig["labelFontSize"] = "24"
    chartConfig["defaultcenterLabelFont"] = "Source Han Sans K"
    chartConfig["defaultcenterlabelFontBlod"] = "70"
    chartConfig["aligncaptionwithcanvas"] = "0"
    chartConfig["captionpadding"] = "0"
    chartConfig["decimals"] = "1"
    chartConfig["plottooltext"] = "<b>$percentValue</b>"
    chartConfig["labelFont"] = "Source Han Sans K"
    chartConfig["labelFontSize"] = "22"
    chartConfig["labelFontBold"] = "70"
    chartConfig["centerlabel"] = "$label  $value"
    chartConfig["theme"] = "fusion"
    chartConfig["numberSuffix"] = "K"

    # The `chartData` dict contains key-value pairs data
    chartData = OrderedDict()
    count = 0
    for stock in stock_data:
        count = count%len(colorcode)
        chartData[stock.name] = [stock.profit_asset, colorcode[count]]
        count += 1
    # chartData["서연이화"] = [43.3, "#3C42D6"]
    # chartData["카카오"] = [19.2, "#7479FF"]
    # chartData["네이버 주식회사"] = [17, "#BBD3FC"]
    # chartData["비트코인"] = [6.5, "#DEEAFF"]

    dataSource["chart"] = chartConfig
    dataSource["data"] = []

    for label, value in chartData.items():
        data = {}
        data["label"] = label
        data["value"] = value[0]
        data["color"] = value[1]
        dataSource["data"].append(data)


    # Create an object for the column 2D chart using the FusionCharts class constructor
    # The chart data is passed to the `dataSource` parameter.
    column2D = FusionCharts("doughnut2d", "ex1" , "1000", "650", "chart-1", "json", dataSource)
    return column2D

# fusion chart_final - Donut
def fusion_donut_final(name,profit, sum_data):
    colorcode = ['#3C42D6','#5359FF','#7479FF','#8B8FFF','#A8ABFF','#C6C8FF','#BBD3FC','#DEEAFF','#ECF3FF', '#FFFFFF']


    dataSource = OrderedDict()

    chartConfig = OrderedDict()
    chartConfig["chartBottomMargin"] = "100"
    chartConfig["bgColor"] = "#F5F9FF"
    chartConfig["showpercentvalues"] = "1"
    chartConfig["legendPosition"] = "right"
    chartConfig["legendCaption"] = "종목별 비중"
    chartConfig["legendCaptionBold"] = "1"
    chartConfig["legendCaptionFont"] = "Source Han Sans K"
    chartConfig["legendCaptionFontSize"] = "28"
    chartConfig["legendCaptionFontColor"] = "#4A536A"
    chartConfig["legendIconScale"] = "2"
    chartConfig["legendItemFontBold"] = "70"
    chartConfig["legendItemFont"] = "Source Han Sans K"
    chartConfig["legendItemFontColor"] = "#000000"
    chartConfig["legendItemFontSize"] = "20"
    chartConfig["defaultcenterlabel"] = str(sum_data)
    chartConfig["centerLabelFontSize"] = "24"
    chartConfig["labelFontSize"] = "24"
    chartConfig["aligncaptionwithcanvas"] = "0"
    chartConfig["captionpadding"] = "0"
    chartConfig["decimals"] = "1"
    chartConfig["plottooltext"] = "<b>$percentValue</b>"
    chartConfig["centerlabel"] = "$label: $value"
    chartConfig["theme"] = "fusion"
    chartConfig["numberSuffix"] = "K"

    # The `chartData` dict contains key-value pairs data
    chartData = OrderedDict()
    count = 0
    for n,p in zip(name, profit):
        count = count%len(colorcode)
        chartData[n] = [p, colorcode[count]]
        count += 1
    # chartData["서연이화"] = [43.3, "#3C42D6"]
    # chartData["카카오"] = [19.2, "#7479FF"]
    # chartData["네이버 주식회사"] = [17, "#BBD3FC"]
    # chartData["비트코인"] = [6.5, "#DEEAFF"]

    dataSource["chart"] = chartConfig
    dataSource["data"] = []

    for label, value in chartData.items():
        data = {}
        data["label"] = label
        data["value"] = value[0]
        data["color"] = value[1]
        dataSource["data"].append(data)


    # Create an object for the column 2D chart using the FusionCharts class constructor
    # The chart data is passed to the `dataSource` parameter.
    column2D = FusionCharts("doughnut2d", "ex1" , "1000", "650", "chart-1", "json", dataSource)
    return column2D


# Line2D 그래프 그리기
def fusion_line(month, result_price):

    # Chart data is passed to the `dataSource` parameter, as dictionary in the form of key-value pairs.
    dataSource = OrderedDict()

    # The `chartConfig` dict contains key-value pairs data for chart attribute
    chartConfig = OrderedDict()
    chartConfig["caption"] = "BackTesting"
    chartConfig["subCaption"] = "과거 시점부터 오늘날짜까지의 수익률 확인그래프"
    chartConfig["xAxisName"] = "date"
    chartConfig["yAxisName"] = "stock price(won)"
    chartConfig["theme"] = "fusion"

    # The `chartData` dict contains key-value pairs data
    chartData = OrderedDict()
    for m, p in zip(month, result_price):
        chartData[m] = p
    # chartData["Venezuela"] = 290
    # chartData["Saudi"] = 260
    # chartData["Canada"] = 180
    # chartData["Iran"] = 140
    # chartData["Russia"] = 115
    # chartData["UAE"] = 100
    # chartData["US"] = 30
    # chartData["China"] = 30


    dataSource["chart"] = chartConfig
    dataSource["data"] = []

    # Convert the data in the `chartData` array into a format that can be consumed by FusionCharts.
    # The data for the chart should be in an array wherein each element of the array is a JSON object
    # having the `label` and `value` as keys.

    # Iterate through the data in `chartData` and insert in to the `dataSource['data']` list.
    for key, value in chartData.items():
        data = {}
        data["label"] = key
        data["value"] = value
        dataSource["data"].append(data)


    # Create an object for the column 2D chart using the FusionCharts class constructor
    # The chart data is passed to the `dataSource` parameter.
    Line2D = FusionCharts("line", "ex1" , "1200", "800", "chart-1", "json", dataSource)

    return  Line2D