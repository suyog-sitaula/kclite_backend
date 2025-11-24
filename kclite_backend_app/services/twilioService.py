from twilio.rest import Client
import os
from ..util.redis_client import redis_client
import json
from ..util.twilio_client import TwilioClient
class CreateTwilioSubAccount:
    def subAccount(friendly_name):
        client = TwilioClient.get_client()
        sub_account = client.api.v2010.accounts.create(friendly_name=friendly_name)
        return sub_account.sid
    
class twilioService:
    def __init__(self, user_sub_account_sid=None):
        try:
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
            return {"success": True, "data": sub_sid}
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
            return {"success": True, "data": validation_request.sid}
        except Exception as e:
            raise Exception(f"Error verifying number: {e}")

    def createNewTrunk(self,connection_policy_sid):
        try:
            byoc_trunk = self.client.voice.v1.byoc_trunks.create(
                friendly_name="KCLite User BYOC Trunk",
                ConnectionPolicySid=connection_policy_sid
            )
            return {"success": True, "data": byoc_trunk.sid}
        except Exception as e:
            raise Exception(f"Error creating new trunk: {e}")
    
    def sipDomain(self, sip_domain,byoc_trunk_sid):
        try:
            sip_credential_list = self.client.sip.domains.create(
                domainName=sip_domain,
                byocTrunkSid= byoc_trunk_sid
            )
            return {"success": True, "data": sip_credential_list.sid}
        except Exception as e:  
            raise Exception(f"Error creating SIP domain: {e}")
    
    def originationConnectionPolicy(self, sub_account_sid=None):
        try:
            if sub_account_sid:
                sub_client = self.client.api.v2010.accounts(sub_account_sid)
                origination_connection_policy = sub_client.voice.v1.connection_policies.create()
            else:
                raise Exception("Error finding the sub account for this user.")
            return {"success": True, "data": origination_connection_policy}
        except Exception as e:
            raise Exception(f"Error creating origination connection policy: {e}")
    
    def addIPToACL(self, acl_sid, ip_address):
        try:
            ip_address_obj = self.client.trunking.v1.ip_access_control_lists(acl_sid).ip_addresses.create(
                friendly_name="KCLite User IP Address",
                ip_address=ip_address
            )
            return {"success": True, "data": ip_address_obj.sid}
        except Exception as e:
            raise Exception(f"Error adding IP to ACL: {e}")
    
    def ipAccessControlList(self, trunk_sid, friendly_name="KCLite ACL"):
        try:
            acl = self.client.trunking.v1.trunks(trunk_sid).ip_access_control_lists.create(
                friendly_name=friendly_name
            )
            return {"success": True, "data": acl.sid}
        except Exception as e:
            raise Exception(f"Error creating IP Access Control List: {e}")