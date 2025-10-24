from django.db import models

# Create your models here.
class SubscriptionPlans(models.Model):
    plan_name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    duration_days = models.IntegerField()
    expiry_date = models.DateField()
    total_credits = models.IntegerField()
    credits_left = models.IntegerField()

    def __str__(self):
        return self.plan_name
    
class Users(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=150, unique=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    twilio_token = models.CharField(max_length=100, unique=True)
    subscription_id = models.ForeignKey(SubscriptionPlans, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.username
    
class NumberDetails(models.Model):
    user_id = models.ForeignKey(Users, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    expiry_date = models.DateField()
    purchase_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.user.username} - {self.phone_number}"
    

class BillingInfo(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    card_number = models.CharField(max_length=16)
    expiry_date = models.DateField()
    cvv = models.CharField(max_length=4)

    def __str__(self):
        return f"Billing Info for {self.user.username}"
    
class Logs(models.Model):
    number_id = models.ForeignKey(NumberDetails, on_delete=models.CASCADE)
    action_type = models.CharField(max_length=100)
    destination_number = models.CharField(max_length=15)
    source_number = models.CharField(max_length=15)
    duration_seconds = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Log for {self.user.username} at {self.timestamp}"
    
class Contacts(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    contact_name = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=15)
    email = models.EmailField(null=True, blank=True)
    business = models.CharField(max_length=100, null=True, blank=True)
    
    def __str__(self):
        return f"{self.contact_name} - {self.contact_number}"