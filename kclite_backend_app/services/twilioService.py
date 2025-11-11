from twilio.rest import Client
import os
from util.redis_client import redis_client
import json
class twilioService:
    def __init__(self):
        account_sid = os.environ["TWILIO_ACCOUNT_SID"]
        auth_token = os.environ["TWILIO_AUTH_TOKEN"]
        self.client = Client(account_sid, auth_token)

    def subAccount(self, friendly_name):
        sub_account = self.client.api.v2010.accounts.create(friendly_name=friendly_name)
        return sub_account.sid

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

    def createNewTrunk(self, friendly_name, sub_account_sid=None):
        if sub_account_sid:
            sub_client = self.client.api.v2010.accounts("ACXXXX-SUBACCOUNT-SID-XXXX")
            byoc_trunk = sub_client.voice.v1.byoc_trunks.create()
        else:
            trunk = self.client.trunking.trunks.create(friendly_name=friendly_name)
        return byoc_trunk.sid
    