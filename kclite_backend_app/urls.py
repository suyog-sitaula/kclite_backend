from django.urls import path
from . import views

urlpatterns = [
    path('all_numbers/', views.AllNewNumberView.as_view(), name='all_numbers'),
    path('verification_status/', views.VerificationCompletion.as_view(), name='verification_status'),
]