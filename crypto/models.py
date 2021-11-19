from django.db import models
from django.utils import timezone
from authentication.models import Account
from .crypto_utils import crypto

class CryptoTicker(models.Model):
    name = models.CharField(verbose_name="종목 이름", max_length=20)
    ticker = models.CharField(verbose_name="티커", max_length=20)
    market = models.CharField(verbose_name="마켓", max_length=20)
    def current_value(self):
        return crypto.get_current_price(self.ticker)
    def __str__(self) -> str:
        return self.name
class Crypto(models.Model):
    account = models.ForeignKey(Account, verbose_name="계정", on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now, null=True)
    name = models.CharField(verbose_name="종목 이름", max_length=20, default="default_name")
    ticker = models.CharField(verbose_name="티커", max_length=20)
    market = models.CharField(verbose_name="마켓", max_length=20, default="defalut_market")
    quantity = models.FloatField(verbose_name="보유량",default=0)
    buy_price = models.FloatField(verbose_name="매수가격", default=0)

    def current_value(self):
        return crypto.get_current_price(self.ticker)

    def total_buy_amount(self):
        return self.buy_price * self.quantity

    def total_value(self):
        now_price = crypto.get_current_price(self.ticker)
        return round(self.quantity*now_price,2)
    
    def profit_rate(self):
        profit_rate = round(float((self.total_value()-(self.total_buy_amount()))/self.total_buy_amount()*100),2)
        return profit_rate

    def __str__(self) -> str:
        return self.account.nickname +"-"+ self.ticker