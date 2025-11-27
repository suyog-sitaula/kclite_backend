from rest_framework import serializers  
from .models import Users, NumberDetails, BillingInfo, Logs, SubscriptionPlans, TelecomProfile, Contacts

class SubscriptionPlansSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlans
        fields = ['plan_name', 'price','description']

class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['full_name', 'email', 'is_active', 'total_credits', 'credits_left', 'duration_days', 'expiry_date', 'subscription']
        read_only_fields = ['date_joined']
        
    def validate_email(self, value):
        if Users.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        if value.count('@') != 1 or '.' not in value.split('@')[1]:
            raise serializers.ValidationError("Enter a valid email address.")
        return value
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