from django.urls import path
from . import views

urlpatterns = [
    path("login/",views.login,name="login"),
    path("register_step1/",views.register1,name="register1"),
]
