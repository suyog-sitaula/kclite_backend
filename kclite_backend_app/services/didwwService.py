from django.conf import settings
from .didww_sdk.client import DidwwClient
from .didww_sdk.exceptions import DidwwAPIError
from .. import models as Models
from .twilioService import twilioService
class DIDWWService:
    def __init__(self):
        self.client = DidwwClient()

    def new_number(self, urn, country_code, group_type, quantity=1):
        try:
            twilioService.verifyNumber(urn)
            return self.client.buy_number(did_id= urn)
        except DidwwAPIError as e:
            print(f"Error purchasing number: {e}")
            return None 
    def getAllNumbers(self):
        try:
            numbers = self.client.list_available_dids(country="MX")
            return numbers
        except DidwwAPIError as e:
            print(f"Error retrieving numbers: {e}")
            return None
    def getExistingNumbers(self):
        try:
            numbers = Models.NumberDetails.objects.all()
            return None
        except DidwwAPIError as e:
            print(f"Error retrieving numbers: {e}")
            return None
    
    def attachNumberToTrunk():
        pass

    