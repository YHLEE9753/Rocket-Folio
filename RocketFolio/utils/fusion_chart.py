from collections import OrderedDict
from stock.fusioncharts import FusionCharts

# fusion chart - Donut
    # asset_name_list : 자산 이름 리스트
    # asset_amount_list : 현재 종목별 자산별 금액 리스트 
    # total_amount_str : 총자산 ,구분자 추가해서
def fusion_donut(asset_name_list, asset_amount_list, total_amount_str): 
    colorcode = ['#08298A','#0080FF','#045FB4','#0404B4','#00BFFF','#4000FF','#58D3F7','#819FF7','#08298A']
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
    chartConfig["defaultcenterlabel"] = str(total_amount_str)
    chartConfig["aligncaptionwithcanvas"] = "0"
    chartConfig["captionpadding"] = "0"
    chartConfig["decimals"] = "1"
    chartConfig["plottooltext"] = "<b>$percentValue</b>"
    chartConfig["centerlabel"] = "$label: $value"
    chartConfig["theme"] = "fusion"
    chartConfig["numberSuffix"] = "K"

    # The `chartData` dict contains key-value pairs data
    chartData = OrderedDict()

    if len(asset_name_list) != len(asset_amount_list):
        raise Exception

    count = 0
    for i in range(len(asset_name_list)):
        count = count%len(colorcode)
        chartData[asset_name_list[i]] = [asset_amount_list[i], colorcode[count]]
        count += 1

    dataSource["chart"] = chartConfig
    dataSource["data"] = []

    for key in chartData.keys():
        data = {}
        data["label"] = key
        data["value"] = chartData[key][0]
        data["color"] = chartData[key][1]
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
    chartConfig["subCaption"] = "과거 시점에서의 수익률 확인그래프"
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