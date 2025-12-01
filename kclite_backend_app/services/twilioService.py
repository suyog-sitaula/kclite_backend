from django.conf import settings
from twilio.rest import Client
import os

from kclite_backend_app.serializers import TelecomProfileSerializer
from ..util.redis_client import redis_client
import json
from ..util.twilio_client import TwilioClient
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VoiceGrant
from ..models import Users, TelecomProfile

#save the required details in the database using serializer after creating new keys or account 
class CreateTwilioSubAccount:
    def subAccount(friendly_name):
        client = TwilioClient.get_client()
        sub_account = client.api.v2010.accounts.create(friendly_name=friendly_name)
        return sub_account.sid
    
class twilioService:
    def __init__(self, user_sub_account_sid=None):
        try:
            self.ip_addresses = settings.DIDWW_ALLOWED_RTP_ADDRESS
            self.client = TwilioClient.get_client()
            self.sub_account_sid = user_sub_account_sid
            if not user_sub_account_sid:
                subAccountClass = CreateTwilioSubAccount()
                self.sub_account_sid = subAccountClass.subAccount("KCLite User Sub Account")
            self.sub_client = self.client.api.v2010.accounts(self.sub_account_sid)
        except Exception as e:
            raise Exception(f"Error initializing Twilio client: {e}")
        
    def getSubAccountDetails(self):
        try:
            sub_sid = self.sub_client.fetch().sid
            return {"success": True, "sub_acccount_sid": sub_sid}
        except Exception as e:
            raise Exception(f"Error fetching sub account details: {e}")
    
    def verifyNumber(self, number):
        try:
            validation_request = self.client.validation_requests.create(
            friendly_name="Third Party VOIP Number",
            phone_number=number,
            status_callback="https://9538b5e79b33.ngrok-free.app/kclite/verification_status/",
            )
            print(validation_request.account_sid)
            redis_client.set(f"validation_{number}", json.dumps({
                "validation_code": validation_request.validation_code}))
            return {"success": True, "validation_request_sid": validation_request.sid}
        except Exception as e:
            raise Exception(f"Error verifying number: {e}")

    def originationConnectionPolicy(self, sub_account_sid=None):
        try:
            if sub_account_sid:
                sub_client = self.client.api.v2010.accounts(sub_account_sid)
                origination_connection_policy = sub_client.voice.v1.connection_policies.create()
            else:
                raise Exception("Error finding the sub account for this user.")
            return {"success": True, "origination_connection_policy_sid": origination_connection_policy.sid}
        except Exception as e:
            raise Exception(f"Error creating origination connection policy: {e}")

    
    def createNewTrunk(self,connection_policy_sid):
        try:
            byoc_trunk = self.client.voice.v1.byoc_trunks.create(
                friendly_name="KCLite User BYOC Trunk",
                ConnectionPolicySid=connection_policy_sid
            )
            return {"success": True, "byoc_trunk_sid": byoc_trunk.sid}
        except Exception as e:
            raise Exception(f"Error creating new trunk: {e}")
    
    def updateSIPDomain(self, sip_domain_sid,acl_sid):
        try:
            sip_domain = self.client.sip.domains(sip_domain_sid).ip_access_control_list_mappings.create(ip_access_control_list_sid=acl_sid)
            return {"success": True, "sip_domain_sid": sip_domain.sid}
        except Exception as e:
            raise Exception(f"Error updating SIP domain: {e}")
        
    def ipAccessControlList(self, friendly_name="KCLite ACL"):
        try:
            acl = self.client.sip.ip_access_control_lists.create({friendly_name:'KCLite ACL'})
            return {"success": True, "acl_sid": acl.sid}
        except Exception as e:
            raise Exception(f"Error creating IP Access Control List: {e}")

    def addIPToACL(self):
        new_ip_control_list = self.ipAccessControlList()
        acl_sid = new_ip_control_list["acl_sid"]
        try:
            for ip in self.ip_addresses:
                ip_address = self.client.sip.ip_access_control_lists(acl_sid).ip_addresses.create(
                    friendly_name=f'IP {ip}',
                    ip_address=ip
                )
            return {"success": True, "acl_id": acl_sid}
        except Exception as e:
            raise Exception(f"Error adding IP to ACL: {e}")
        
    def sipDomain(self, sip_domain,byoc_trunk_sid):
        try:
            acl_sid = self.addIPToACL()
            sip_credential_list = self.client.sip.domains.create(
                domainName=sip_domain,
                byocTrunkSid= byoc_trunk_sid
            )
            updated_sip_domain = self.updateSIPDomain(sip_credential_list.sid, acl_sid=acl_sid["acl_id"])
            return {"success": True, "sip_credential_list_sid": updated_sip_domain["sip_domain_sid"]}
        except Exception as e:  
            raise Exception(f"Error creating SIP domain: {e}")
    
    def createNewKeys(self):
        api_key = self.sub_client.newKeys.create(friendly_name="KCLite User API Key")
        application = self.sub_client.applications.create(friendly_name="Phone Me",)
        #save in database using serializer
        return {"success": True, "data": {"api_key_sid": api_key.sid, "api_key_secret": api_key.secret, "twiml_app_sid": application.sid}}
    
    def generateToken(self, identity, user_id,ttl=3600):
        try:
            twilio_credentials = TelecomProfile.objects.get(user__id=user_id)
            serialized_telecom_profile = TelecomProfileSerializer(twilio_credentials)
            twilio_credentials_data = serialized_telecom_profile.data
            twilio_api_key_sid = twilio_credentials_data['twilio_api_key_sid']
            twilio_subaccount_sid = twilio_credentials_data['twilio_subaccount_sid']
            outgoing_application_sid = twilio_credentials_data['twilio_twiml_app_sid']
            twilio_api_key_secret = twilio_credentials_data['twilio_api_key_secret']
            token = AccessToken(twilio_subaccount_sid, twilio_api_key_sid, twilio_api_key_secret, identity=identity, ttl=ttl)

            voice_grant = VoiceGrant(
                outgoing_application_sid=outgoing_application_sid,
                incoming_allow=True
            )
            token.add_grant(voice_grant)
            return {"success": True, "token":token.to_jwt()}
        
        except Exception as e:
            raise Exception(f"Error generating token: {e}")
    
    