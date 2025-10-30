from django.conf import settings
from .didww_sdk.client import DidwwClient
from .didww_sdk.exceptions import DidwwAPIError
from .. import models as Models
from .twilioService import twilioService
class DIDWWService:
    def __init__(self):
        self.client = DidwwClient()

    def buy_new_number(self, urn,number):
        try:
            bought_id = self.client.buy_number(did_id= urn)
            twilio_service = twilioService(number)
            twilio_service.verifyNumber(urn)
            return bought_id
        except DidwwAPIError as e:
            print(f"Error purchasing number: {e}")
            return None 
    def getAllNumbers(self):
        try:
            numbers = self.client.list_available_dids(country="US")
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

    