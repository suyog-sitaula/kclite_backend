from twilio.rest import Client
import os
from util.redis_client import redis_client
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


    