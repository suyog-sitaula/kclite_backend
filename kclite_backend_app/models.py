from django.db import models

#bring changes in the model
class SubscriptionPlans(models.Model):
    plan_name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    descripton = models.TextField(blank=True, null=True)
    def __str__(self):
        return self.plan_name


class Users(models.Model):
    """
    App-level user / lead model for Apple Sign-In only.
    No local password or username.
    """

    # Main identifier in your system
    email = models.EmailField(unique=True)
    total_credits = models.IntegerField(default=0)
    credits_left = models.IntegerField(default=0)
    duration_days = models.IntegerField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    # For leads / display
    full_name = models.CharField(max_length=150, blank=True, null=True)

    # Stable Apple-provided ID (from the `sub` claim in the Apple ID token)
    apple_sub = models.CharField(
        max_length=255,
        unique=True,
        blank=True,
        null=True,
        help_text="Unique Apple user identifier (sub claim).",
    )

    date_joined = models.DateTimeField(auto_now_add=True)

    # If you still want to connect subscription plans:
    subscription = models.ForeignKey(
        SubscriptionPlans,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
    )

    def __str__(self):
        # For admin / debugging
        return self.full_name or self.email

class TelecomProfile(models.Model):
    """
    Per-user Twilio/DIDWW configuration.
    One Twilio subaccount per user lives here.
    """
    user = models.OneToOneField(Users, on_delete=models.CASCADE, related_name="telecom_profile")

    twilio_subaccount_sid = models.CharField(max_length=64, blank=True, null=True, unique=True)
    twilio_api_key_sid = models.CharField(max_length=64, blank=True, null=True)
    twilio_api_key_secret = models.CharField(max_length=128, blank=True, null=True)  # store encrypted!
    twilio_twiml_app_sid = models.CharField(max_length=64, blank=True, null=True)
    default_caller_id = models.CharField(max_length=32, blank=True, null=True)  # E.164
    didww_customer_id = models.CharField(max_length=64, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Telecom profile for {self.user}"

class NumberDetails(models.Model):
    """
    One row per purchased DID/phone number.
    Holds both DIDWW and Twilio/BYOC-related configuration.
    """
    STATUS_CHOICES = [
        ("pending_verification", "Pending Verification"),
        ("active", "Active"),
        ("failed", "Failed"),
        ("suspended", "Suspended"),
    ]

    user = models.ForeignKey(Users, null=True, blank=True, on_delete=models.CASCADE, related_name="numbers")

    phone_number = models.CharField(max_length=20)         
    did_urn = models.CharField(max_length=128,null=True, blank=True,)         
    inbound_trunk_id = models.CharField(max_length=100, blank=True, null=True)
    outbound_trunk_id = models.CharField(max_length=100, blank=True, null=True)
    sip_uri = models.CharField(max_length=255, blank=True, null=True)

    ip_address = models.GenericIPAddressField(blank=True, null=True)

    verification_sid = models.CharField(max_length=100, blank=True, null=True)
    verification_status = models.CharField(
        max_length=32,
        choices=[
            ("pending", "Pending"),
            ("in_progress", "In Progress"),
            ("verified", "Verified"),
            ("failed", "Failed"),
        ],
        default="pending",
    )

    connection_policy_sid = models.CharField(max_length=64, blank=True, null=True)
    byoc_trunk_sid = models.CharField(max_length=64, blank=True, null=True)
    sip_domain = models.CharField(max_length=255, blank=True, null=True)
    sip_domain_sid = models.CharField(max_length=64, blank=True, null=True)
    acl_sid = models.CharField(max_length=64, blank=True, null=True)

    expiry_date = models.DateField(blank=True, null=True)
    purchase_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default="pending_verification")

    def __str__(self):
        return f"{self.user.username} - {self.phone_number}"

class BillingInfo(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="billing_infos")
    card_last4 = models.CharField(max_length=4)
    card_brand = models.CharField(max_length=20, blank=True, null=True)
    payment_provider_customer_id = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Billing Info for {self.user.username}"

class Logs(models.Model):
    """
    Basic call log / action log.
    You can extend this later with provider-specific fields (Twilio SIDs, etc.).
    """
    number = models.ForeignKey(NumberDetails, null=True, blank=True, on_delete=models.CASCADE, related_name="logs")
    user = models.ForeignKey(Users, null=True, blank=True, on_delete=models.CASCADE, related_name="logs")

    action_type = models.CharField(max_length=100)  # e.g. 'call', 'sms', 'verification'
    direction = models.CharField(
        max_length=16,
        choices=[("inbound", "Inbound"), ("outbound", "Outbound")],
        blank=True,
        null=True,
    )
    twilio_call_sid = models.CharField(max_length=64, blank=True, null=True)

    destination_number = models.CharField(max_length=20)
    source_number = models.CharField(max_length=20)
    duration_seconds = models.IntegerField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Log for {self.user.username} at {self.timestamp}"

class Contacts(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="contacts")
    contact_name = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=20)
    email = models.EmailField(null=True, blank=True)
    business = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.contact_name} - {self.contact_number}"