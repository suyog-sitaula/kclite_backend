
from ..services.didwwService import DIDWWService
from ..services.twilioService import twilioService
class NumberPurchaseController:
    def __init__(self):
        try:
            self.didww_service = DIDWWService()
            self.twilio_service = twilioService()
        except Exception as e:
            raise Exception(f"Error initializing services: {e}")
        
    def numberPurchaseFlow(self, urn, number,username,sip_domain_host):
        try:
            new_number = self.didww_service.buyNewNumber(urn)
            number_id = new_number["data"]
            
            inbound_trunk = self.didww_service.createInboundTrunk(username,sip_domain_host)
            inbound_trunk_id = inbound_trunk["inbound_trunk_id"]
            sip_uri = inbound_trunk["sip_uri"]

            outbound_trunk = self.didww_service.createOutboundTrunk()
            outbound_trunk_id = outbound_trunk["outbound_trunk_id"]

            verification = self.twilio_service.verifyNumber(urn)
            verification_sid = verification["data"]
            
            return {"first_phase_verification_status": True, "data": {
                "number_id": number_id,
                "inbound_trunk_id": inbound_trunk_id,
                "number":number,
                "sip_uri": sip_uri,
                "outbound_trunk_id": outbound_trunk_id,
                "verification_sid": verification_sid
            }}
        except Exception as e:
            return {"first_phase_verification_status": False, "error": str(e)}
    
    def twilioAccountCreationAndTrunkSetup(self, sip_domain, ip_address):
        try:
            sub_account = self.twilio_service.getSubAccountDetails()
            sub_account_sid = sub_account["data"]
            
            origination_policy = self.twilio_service.originationConnectionPolicy(sub_account_sid)
            origination_policy_sid = origination_policy["data"]
            
            byoc_trunk = self.twilio_service.createNewTrunk(origination_policy_sid)
            byoc_sid = byoc_trunk["data"]
            
            sip_domain_obj = self.twilio_service.sipDomain(sip_domain, byoc_sid)
            sip_domain_sid = sip_domain_obj["sip_credential_list_sid"]
            
            return {"success": True, "data": {
                "sub_account_sid": sub_account_sid,
                "byoc_trunk_sid": byoc_sid,
                "sip_domain": sip_domain,
                "sip_domain_sid": sip_domain_sid,

            }}
        except Exception as e:
            raise Exception(f"Error in Twilio account creation and trunk setup: {e}")
    
    def appCreationAndKeySetup(self, user_id):
        try:
            new_keys = self.twilio_service.createNewKeys(user_id)
            return {"success": True, "data": new_keys["data"]}
        except Exception as e:
            raise Exception(f"Error in app creation and key setup: {e}")
        
    def numberPurchaseFlowAfterVerification(self, sip_domain, urn, number,username,password):
        twili_setup = self.twilioAccountCreationAndTrunkSetup(sip_domain=sip_domain, ip_address=number.ip_address)
        app_creation = self.appCreationAndKeySetup()
        update_inbound = self.didww_service.update_inboundTrunk(urn, sip_domain,username,password)
        attach_number = self.didww_service.attachNumberToTrunk()
        return {"success": True, "data": "Number purchase and trunk setup completed."}