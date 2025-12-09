from django.conf import settings
from jwt import PyJWKClient
import jwt
from ..models import Users
class AuthService:
    def __init__(self, user_repository, token_service):
        self.user_repository = user_repository
        self.token_service = token_service
        
         # Apple config
        self.apple_jwks_url = settings.APPLE_JWKS_URL
        self.apple_issuer = settings.APPLE_ISSUER
        self.apple_audience = settings.APPLE_AUDIENCE
        self.jwks_client = PyJWKClient(self.apple_jwks_url)


    def verifyAppleIdToken(self, apple_token):
        # Logic to verify Apple ID token
        if not apple_token:
            raise ValueError("Missing Apple identity token")

        # 1. Get signing key from Apple’s JWKS
        signing_key = self.jwks_client.get_signing_key_from_jwt(apple_token)

        # 2. Decode & validate token
        decoded = jwt.decode(
            apple_token,
            signing_key.key,
            algorithms=["RS256"],
            audience=self.apple_audience,
            issuer=self.apple_issuer,
        )

        return decoded
        
    
    def authenticate_user(self, decoded_token):
        user_sub = decoded_token.get("sub")
        email = decoded_token.get("email", "")
        user, created = Users.objects.get_or_create(
            apple_sub=user_sub,
            defaults={
                "email": email,
            },
        )
        if created:
            return {"new_user": True, "user": user}
        return {"new_user": False, "user": user}
    
        

