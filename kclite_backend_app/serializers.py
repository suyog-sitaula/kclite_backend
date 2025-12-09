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
        read_only_fields = ['date_joined', 'public_id', 'apple_sub']
        
    def validate_email(self, value):
        if Users.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        if value.count('@') != 1 or '.' not in value.split('@')[1]:
            raise serializers.ValidationError("Enter a valid email address.")
        return value
    
class NumberDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = NumberDetails
        fields = ['status_choices', 'phone_number', 'did_urn', 'inbound_trunk_id', 'outbound_trunk_id', 'sip_uri', "ip_address", 'verification_sid', 'verification_status', 'connection_policy_sid', 'byoc_trunk_sid', 'sip_domain', 'sip_domain_sid', 'acl_sid', 'expiry_date', 'purchase_date', 'status']
    def validate_phone_number(self, value):
        qs = NumberDetails.objects.filter(phone_number=value)

        # If updating, ignore the current instance
        if self.instance is not None:
            qs = qs.exclude(pk=self.instance.pk) 

        if qs.exists():
            raise serializers.ValidationError(
                "This phone number already exists in the system."
            )
        return value
class BillingInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillingInfo
        fields = '__all__'

class LogsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Logs
        fields = ['number', 'user', 'action_type','direction', 'twilio_call_sid', 'destination_number', 'source_number', 'duration_seconds']
        read_only_fields = ['timestamp']
        
class TelecomProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelecomProfile
        fields = ['user', 'twilio_subaccount_sid','twilio_api_key_sid', 'twilio_api_key_secret', 'twilio_twiml_app_sid', 'default_caller_id', 'didww_customer_id']
        read_only_fields = ['created_at','updated_at']
        
class ContactsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contacts
        fields = ['user', 'contact_name', 'contact_number','email', 'business']
    def validate_contact_number(self, value):
        if Contacts.objects.filter(contact_number=value).exists():
            raise serializers.ValidationError("This contact number already exists in the system.")
        return value
    def validate_email(self, value):
        if Users.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        if value.count('@') != 1 or '.' not in value.split('@')[1]:
            raise serializers.ValidationError("Enter a valid email address.")