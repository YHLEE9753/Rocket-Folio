from django.contrib import admin
from django.urls import path,include
from authentication.views import login
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', login, name = 'main'),
    path('authentication/',include('authentication.urls')),
    path('accounts/', include('allauth.urls')),
    path('stock/', include('stock.urls')),
    path('portfolio/',include('portfolio.urls')),
    path('crypto/',include('crypto.urls')),
    path('stock/', include('stock.urls')),
]
