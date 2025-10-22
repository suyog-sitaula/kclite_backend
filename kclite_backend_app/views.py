from django.shortcuts import render

# Create your views here.
def index(self, request):
    return render(request, 'home.html')  
    
def inbounding(request):
    return render(request, 'inbounding.html')

def outbounding(request):
    return render(request, 'outbounding.html')

def subscription(request):
    return render(request, 'subscription.html')
