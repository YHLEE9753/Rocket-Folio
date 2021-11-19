from import_export import resources
from .models import Stockhistory

class StockResource(resources.ModelResource):
    class Meta:
        model = Stockhistory