import pyupbit


def get_current_price(ticker):
    '''
    parameter : 티커
    return : 현재 가격 
    '''
    current_price = pyupbit.get_current_price(f"KRW-{ticker}")
    print(f"{ticker} current_price : {current_price}")
    return float(current_price)
