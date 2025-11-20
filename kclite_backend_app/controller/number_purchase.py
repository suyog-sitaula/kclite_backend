
from ..services.didwwService import DIDWWService
from ..services.twilioService import twilioService
class NumberPurchaseController:
    def __init__(self):
        self.didww_service = DIDWWService()
        self.twilio_service = twilioService()
        
    def numberPurchaseFlow(self, urn, number,username,sip_domain_host):
        result = self.didww_service.buyNewNumber(urn)
        inbound_trunk = self.didww_service.createInboundTrunk(username,sip_domain_host)
        outbound_trunk = self.didww_service.createOutboundTrunk()
        verification = self.twilio_service.verifyNumber(urn)
        return result
    
    def twilioAccountCreationAndTrunkSetup(self, sip_domain, ip_address):
        sub_account = self.twilio_service.getSubAccountDetails()
        origination_policy = self.twilio_service.originationConnectionPolicy(sub_account)
        byoc_trunk = self.twilio_service.createNewTrunk(origination_policy)
        sip_domain_obj = self.twilio_service.sipDomain(sip_domain, byoc_trunk)
        acl_ip = self.twilio_service.addIPToACL(sip_domain_obj, ip_address)
        return {"success": True, "data": {
            "sub_account_sid": sub_account,
            "byoc_trunk_sid": byoc_trunk,
            "sip_domain_sid": sip_domain_obj,
            "acl_ip_sid": acl_ip
        }}
        
    def numberPurchaseFlowAfterVerification(self, urn, number,username,password):
        update_inbound = self.didww_service.update_inboundTrunk(urn, sip_domain_host,username,password)
        attach_number = self.didww_service.attachNumberToTrunk()
        return {"success": True, "data": "Number purchase and trunk setup completed."}