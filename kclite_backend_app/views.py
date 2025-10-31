from django.shortcuts import render
from rest_framework.response import Response
from .services.didwwService import DIDWWService
from rest_framework.views import APIView
# Create your views here.
def index(self, request):
    return render(request, 'home.html')  

class BuyNumberView(APIView):
    def get (self, request):
        uuid = request.query_params.get('uuid')
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
        verification_status = request.data.get('VerificationStatus')
        return Response({"status": verification_status})
    
def inboundingCall(request):
    return render(request, 'inbounding.html')

def outboundingCall(request):
    return render(request, 'outbounding.html')

def subscription(request):
    return render(request, 'subscription.html')

def contact(request):
    return render(request, 'contact.html')