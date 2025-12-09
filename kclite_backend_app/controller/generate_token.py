from ..services.tokenService import TokenService
from ..services.twilioService import twilioService
class TokenGenerateController:
    def __init__(self):
        # self.tokenService = TokenService()
        self.twilioService = twilioService()
        #self.twilioService = twilioService(auto_create_subaccount=True)
    def generateToken(self, user_id):
        token = self.tokenService.create_token(user_id=user_id,identity="identity")
        return token
    
    def generateVoiceToken(self, identity, outgoing_application_sid, twilio_subaccount_sid, twilio_api_key_sid, twilio_api_key_secret, user_id):
        token = self.twilioService.generateToken(
            identity=identity,
            outgoing_application_sid=outgoing_application_sid,
            twilio_subaccount_sid=twilio_subaccount_sid,
            twilio_api_key_sid=twilio_api_key_sid,
            twilio_api_key_secret=twilio_api_key_secret,
            user_id=user_id
        )
        return token
        # return {
        #     "ok": True,
        #     "identity": identity,
        #     "outgoing_application_sid": outgoing_application_sid,
        #     "twilio_subaccount_sid": twilio_subaccount_sid,
        #     "twilio_api_key_sid": twilio_api_key_sid,
        #     "twilio_api_key_secret": twilio_api_key_secret,
        #     "user_id": user_id,
        # }