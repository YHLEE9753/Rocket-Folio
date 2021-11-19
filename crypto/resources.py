from import_export import resources
from .models import CryptoTicker

class CryptoResource(resources.ModelResource):
    class Meta:
        model = CryptoTicker