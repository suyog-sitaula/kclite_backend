from django.shortcuts import render

# Create your views here.
def index(self, request):
    return render(request, 'home.html')  

def newNumber(request):
    return render(request, 'newnumber.html')
    
def inboundingCall(request):
    return render(request, 'inbounding.html')

def outboundingCall(request):
    return render(request, 'outbounding.html')

def subscription(request):
    return render(request, 'subscription.html')

def contact(request):
    return render(request, 'contact.html')