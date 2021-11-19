from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Account(models.Model):
    user = models.OneToOneField(User, verbose_name="유저", on_delete=models.CASCADE)
    register_date = models.DateTimeField(auto_now_add=True, verbose_name='등록날짜')
    nickname = models.CharField(max_length=64, verbose_name='닉네임')
    def __str__(self) -> str:
        return self.nickname
    # 향후 주식, 암호화폐 계좌 정보 등록
