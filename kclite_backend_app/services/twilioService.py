from twilio.rest import Client
import os
from kclite_backend_app.util.redis_client import redis_client
import json
from util.twilio_client import TwilioClient
class CreateTwilioSubAccount:
    def subAccount(friendly_name):
        client = TwilioClient.get_client()
        sub_account = client.api.v2010.accounts.create(friendly_name=friendly_name)
        return sub_account.sid
    
class twilioService:
    def __init__(self, user_sub_account_sid=None):
        self.client = TwilioClient.get_client()
        self.sub_account_sid = user_sub_account_sid
        if not user_sub_account_sid:
            subAccountClass = CreateTwilioSubAccount()
            self.sub_account_sid = subAccountClass.subAccount("KCLite User Sub Account")
        self.sub_client = self.client.api.v2010.accounts(self.sub_account_sid)

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

    def createNewTrunk(self,connection_policy_sid):
        byoc_trunk = self.client.voice.v1.byoc_trunks.create(
            friendly_name="KCLite User BYOC Trunk",
            ConnectionPolicySid=connection_policy_sid
        )
        return byoc_trunk.sid
    
    def sipDomain(self, sip_domain,byoc_trunk_sid):
        sip_credential_list = self.client.sip.domains.create(
            domain_name=sip_domain,
            byoc_trunk_sid= byoc_trunk_sid
        )
        return sip_credential_list.sid
    
    def originationConnectionPolicy(self, sub_account_sid=None):
        if sub_account_sid:
            sub_client = self.client.api.v2010.accounts(sub_account_sid)
            origination_connection_policy = sub_client.voice.v1.byoc_trunks
        else:
            print("No sub account found for this user")
        return origination_connection_policy.sid
    
    def addIPToACL(self, acl_sid, ip_address):
        ip_address_obj = self.client.trunking.v1.ip_access_control_lists(acl_sid).ip_addresses.create(
            friendly_name="KCLite User IP Address",
            ip_address=ip_address
        )
        return ip_address_obj.sid
    
    def ipAccessControlList(self, trunk_sid, friendly_name="KCLite ACL"):
        acl = self.client.trunking.v1.trunks(trunk_sid).ip_access_control_lists.create(
            friendly_name=friendly_name
        )
        return acl.sid