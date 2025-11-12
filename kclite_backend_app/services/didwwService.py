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
            return {"success": True, "data": bought_id}
        except DidwwAPIError as e:
            print(f"Error purchasing number: {e}")
            return {"success": False, "error": str(e)}
    def getAllNumbers(self):
        try:
            numbers = self.client.list_available_dids(country="US")
            return {"success": True, "data": numbers}
        except DidwwAPIError as e:
            print(f"Error retrieving numbers: {e}")
            return {"success": False, "error": str(e)}
    def getExistingNumbers(self):
        try:
            numbers = Models.NumberDetails.objects.all()
            return {"success": True, "data": numbers}
        except DidwwAPIError as e:
            print(f"Error retrieving numbers: {e}")
            return {"success": False, "error": str(e)}
    
    def inboundTrunk(self):
        try:
            inbound_response = self.client.inbound_trunks()
            return {"success":True,"inbound_trunk_id": inbound_response.data.id, "sip_uri": inbound_response.data.attributes.sip_uri}
        except DidwwAPIError as e:
            print(f"Error creating inbound trunk: {e}")
            return {"success": False, "error": str(e)}

    def outboundTrunk(self):
        try:
            outbound_response = self.client.outbound_trunks()
            return {"success":True,"outbound_trunk_id": outbound_response.data.id}
        except DidwwAPIError as e:
            print(f"Error creating outbound trunk: {e}")
            return {"success": False, "error": str(e)}

    def attachNumberToTrunk(self):
        try:
            attach_response = self.client.attach_number_to_trunk()
            return {"success":True,"attach_response_id": attach_response.data.id}
        except DidwwAPIError as e:
            print(f"Error attaching number to trunk: {e}")
            return {"success": False, "error": str(e)}


    