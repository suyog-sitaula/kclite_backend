from django.conf import settings
from didww_sdk.client import DidwwClient
from .didww_sdk.exceptions import DidwwAPIErro
class DIDWWService:
    def __init__(self, api_key, base_url):
        self.client = DidwwClient()

    def new_number(self, urn, country_code, group_type, quantity=1):
        try:
            return self.client.buy_number(did_id= urn)
        except DidwwAPIErro as e:
            print(f"Error purchasing number: {e}")
            return None 
    