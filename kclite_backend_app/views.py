from .controller.number_purchase import NumberPurchaseController
from django.shortcuts import render
from rest_framework.response import Response
from .services.didwwService import DIDWWService
from rest_framework.views import APIView

class BuyNumberView(APIView):
    def get (self, request):
        uuid = request.GET.get('uuid')
        didww_service = DIDWWService()
        purchased_number = didww_service.buy_new_number(urn=uuid)
        
class AllNewNumberView(APIView):
    def get(self, request):
        numbers_with_uuids = []
        didww_service = DIDWWService()
        all_numbers = didww_service.getAllNumbers()
        for number in all_numbers:
            numbers_with_uuids.append({
                "id": number["id"],
                "number": number["attributes"]["number"]
            })
        return Response(numbers_with_uuids)

class VerificationCompletion(APIView):
    def post(self, request):
        call_sid = request.POST.get('CallSid')
        call_status = request.POST.get('CallStatus')
        verification_status = request.POST.get('VerificationStatus')
        
        if call_status == "completed" and verification_status == "approved":
            npc = NumberPurchaseController()
            sip_domain = request.POST.get('sip_domain')
            urn = request.POST.get('urn')
            number = request.POST.get('number')
            username = request.POST.get('username')
            password = request.POST.get('password')
            final_setup = npc.twilioAccountCreationAndTrunkSetup(sip_domain,urn,number,username,password)
        return Response({"status": final_setup["success"], "data": final_setup["data"]})
    
# twilio webhook
class FirstPhaseTrunkSetupView(APIView):
    def __init__(self):
        self.npc = NumberPurchaseController()
    def post(self, request):
        sip_domain = request.POST.get('sip_domain')
        urn = request.POST.get('urn')
        number = request.POST.get('number')
        username = request.POST.get('username')
        
        first_phase_response = self.npc.numberPurchaseFlow(urn, number,username,sip_domain)
        
        return Response(first_phase_response)
    
class InboundingCallView(APIView):
    def post(self, request):
        pass
class outboundingCallView(APIView):
    def post(self, request):
        to_number = request.POST.get("To")

        resp = VoiceResponse()
        dial = resp.dial(caller_id=settings.TWILIO_CALLER_ID)  # your verified / bought number
        if to_number:
            dial.number(to_number)

        return request(str(resp), content_type="text/xml")


def subscription(request):
    return render(request, 'subscription.html')

def contact(request):
    return render(request, 'contact.html')