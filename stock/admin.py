from django.contrib import admin
from .models import Stocklist,Stock,Stockhistory,kospi_kosdaq_history
from import_export.admin import ImportExportModelAdmin
# Register your models here.

@admin.register(Stocklist,Stock,Stockhistory,kospi_kosdaq_history)
class StockAdmin(ImportExportModelAdmin):
    pass
