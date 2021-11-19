from django.db import models
from authentication.models import Account


# Create your models here.
class Stocklist(models.Model):
    company_name = models.CharField(max_length=128, verbose_name='회사이름')
    code = models.CharField(max_length = 32, verbose_name='코드이름')
    # section = models.CharField(max_length = 32, verbose_name='section')
    KOSPI200 = models.BooleanField(default=False)

    def __str__(self):
        return self.company_name


class Stock(models.Model):    
    account = models.ForeignKey(Account, verbose_name="계정", on_delete=models.CASCADE)
    name = models.CharField(max_length=128, verbose_name='주식이름')
    code = models.CharField(max_length = 32, verbose_name='주식코드')
    quantity = models.FloatField(verbose_name='구매 개수')
    buy_price = models.CharField(max_length=128, verbose_name='구매가', blank=True)
    created = models.DateTimeField(auto_now_add=True, verbose_name='구매날짜')
    KOSPI200 = models.BooleanField(default=False)
    
    backtesting_past_price = models.CharField(max_length=128, verbose_name='백테스팅용 과거 가격표', blank=True)
    real_price = models.CharField(max_length=128, verbose_name='실시간가격', blank=True)
    profit_rate = models.CharField(max_length=128, verbose_name='수익률', blank=True)
    profit_asset = models.CharField(max_length=128, verbose_name='주식자산', blank=True)
    property = models.CharField(max_length=128, verbose_name='보유비율', blank=True)

    def __str__(self):
        return self.name

class Stockhistory(models.Model):
    code = models.CharField(max_length=128, verbose_name='code')
    name = models.CharField(max_length =128, verbose_name='name')
    section = models.CharField(max_length=128, verbose_name='section')
    date = models.CharField(max_length=128, verbose_name='date')
    open = models.FloatField(verbose_name='open')
    high = models.FloatField(verbose_name='high')
    low = models.FloatField(verbose_name='low')
    close = models.FloatField(verbose_name='close')

    def __str__(self):
        return self.name+self.date

class kospi_kosdaq_history(models.Model):
    section = models.CharField(max_length=128, verbose_name='section') # Kospi 인지 Kosdaq 인지
    date = models.CharField(max_length=128, verbose_name='date')
    open = models.FloatField(verbose_name='open')
    high = models.FloatField(verbose_name='high')
    low = models.FloatField(verbose_name='low')
    close = models.FloatField(verbose_name='close')

    def __str__(self):
        return self.section+self.date