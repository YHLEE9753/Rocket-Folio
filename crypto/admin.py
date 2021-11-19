from django.contrib import admin
from .models import Crypto, CryptoTicker
from import_export.admin import ImportExportModelAdmin

@admin.register(Crypto,CryptoTicker)
class CryptoAdmin(ImportExportModelAdmin):
    pass