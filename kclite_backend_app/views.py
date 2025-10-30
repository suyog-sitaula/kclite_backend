from django.shortcuts import render
from rest_framework.response import Response
from .services.didwwService import DIDWWService
from rest_framework.views import APIView
# Create your views here.
def index(self, request):
    return render(request, 'home.html')  

def selectedNumber(request, number):

    return render(request, 'selectnumber.html')
class NewNumberView(APIView):
    def get (self, request):
        number = request.query_params.get('number')
        
class AllNewNumberView(APIView):
    def get(self, request):
        didwwService = DIDWWService()
        all_numbers = didwwService.getAllNumbers()
        return Response(all_numbers)

    
def inboundingCall(request):
    return render(request, 'inbounding.html')

def outboundingCall(request):
    return render(request, 'outbounding.html')

def subscription(request):
    return render(request, 'subscription.html')

def contact(request):
    return render(request, 'contact.html')