from django.urls import path
from .views import *

urlpatterns = [
    path('myportfolio/',myPortfolio, name="myportfolio"),
]
