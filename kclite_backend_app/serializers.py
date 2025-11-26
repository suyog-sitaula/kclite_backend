from rest_framework import serializers  
from .models import Users, NumberDetails, BillingInfo, Logs, SubscriptionPlans, TelecomProfile, Contacts

class SubscriptionPlansSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlans
        fields = '__all__'

class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = '__all__'

class NumberDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = NumberDetails
        fields = '__all__'

class BillingInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillingInfo
        fields = '__all__'

class LogsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Logs
        fields = '__all__'
        
class TelecomProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelecomProfile
        fields = '__all__'

class ContactsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contacts
        fields = '__all__'