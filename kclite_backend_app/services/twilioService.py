from twilio.rest import Client
import os
from kclite_backend_app.util.redis_client import redis_client
import json
class twilioService:
    def __init__(self):
        account_sid = os.environ["TWILIO_ACCOUNT_SID"]
        auth_token = os.environ["TWILIO_AUTH_TOKEN"]
        self.client = Client(account_sid, auth_token)

    def verifyNumber(self, number):
        validation_request = self.client.validation_requests.create(
        friendly_name="Third Party VOIP Number",
        phone_number=number,
        status_callback="https://2ad387984f1d.ngrok-free.app/kclite/verification_status/",
        )
        print(validation_request.account_sid)
        redis_client.set(f"validation_{number}", json.dumps({
            "validation_code": validation_request.validation_code}))
        return validation_request.sid
    
    def createSubAccount(self, friendly_name):
        sub_account = self.client.api.v2010.accounts.create(friendly_name=friendly_name)
        return sub_account.sid

    def createByocTrunk(self, friendly_name, sub_account_sid):
        trunk = self.client.voice.v1.byoc_trunks.create(
            friendly_name=friendly_name,
            account_sid=sub_account_sid
        )
        return trunk.sid
    
    def createSipDomain(self):
        domain = self.client.sip.domains.create(
            domain_name="kclite.sip.twilio.com",
                                        )
        return domain.sid   