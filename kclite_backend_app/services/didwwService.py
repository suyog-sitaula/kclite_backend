from django.conf import settings
from .didww_sdk.client import DidwwClient
from .didww_sdk.exceptions import DidwwAPIError
from .. import models as Models
from .twilioService import twilioService
class DIDWWService:
    def __init__(self):
        try:
            self.client = DidwwClient()
        except DidwwAPIError as e:
            raise Exception(f"Error initializing DIDWW client: {e}")
        
    def buyNewNumber(self, urn,number):
        try:
            bought_id = self.client.buy_number(did_id= urn)
            twilio_service = twilioService(number)
            twilio_service.verifyNumber(urn)
            return {"success": True, "data": bought_id}
        except DidwwAPIError as e:
            raise Exception(f"Error buying number: {e}")
        
    def getAllNumbers(self):
        try:
            numbers = self.client.list_available_dids(country="US")
            return {"success": True, "data": numbers}
        except DidwwAPIError as e:
            raise Exception(f"Error retrieving numbers: {e}")
        
    def getExistingNumbers(self):
        try:
            numbers = Models.NumberDetails.objects.all()
            return {"success": True, "data": numbers}
        except DidwwAPIError as e:
            raise Exception(f"Error retrieving existing numbers: {e}")
    
    def createInboundTrunk(self,username,sip_domain_host):
        try:
            inbound_response = self.client.create_inbound_trunks(username,sip_domain_host)
            return {"success":True,"inbound_trunk_id": inbound_response.data.id, "sip_uri": inbound_response.data.attributes.sip_uri}
        except DidwwAPIError as e:
            raise Exception(f"Error creating inbound trunk: {e}")

    def createOutboundTrunk(self):
        try:
            outbound_response = self.client.create_outbound_trunks()
            return {"success":True,"outbound_trunk_id": outbound_response.data.id}
        except DidwwAPIError as e:
            raise Exception(f"Error creating outbound trunk: {e}")

    def update_inboundTrunk(self, inbound_trunk_id, sip_domain_host,username,password):
        try:
            update_response = self.client.update_inbound_trunk(inbound_trunk_id, sip_domain_host,username,password)
            return {"success":True,"update_response_id": update_response.data.id}
        except DidwwAPIError as e:
           raise Exception(f"Error updating inbound trunk: {e}")
        
    def attachNumberToTrunk(self):
        try:
            attach_response = self.client.attach_number_to_trunk()
            return {"success":True,"attach_response_id": attach_response.data.id}
        except DidwwAPIError as e:
            raise Exception(f"Error attaching number to trunk: {e}")


    