from twilio.rest import Client
import os

class twilioService:
    def __init__(self):
        account_sid = os.environ["TWILIO_ACCOUNT_SID"]
        auth_token = os.environ["TWILIO_AUTH_TOKEN"]
        self.client = Client(account_sid, auth_token)

    def verifyNumber(self, number):
        validation_request = self.client.validation_requests.create(
        friendly_name="Third Party VOIP Number",
        phone_number="+14158675310",
        status_callback="https://somefunction.twil.io/caller-id-validation-callback",
        )
        print(validation_request.account_sid)
        return validation_request.sid


    