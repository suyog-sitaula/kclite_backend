import jwt
from datetime import datetime, timedelta, timezone
from django.conf import settings
class TokenService:
    def __init__(self, token_repository):
        self.token_repository = token_repository
        self.expiry_time = 3600  
        self.algorithm = "HS256"
        self.secret_key = settings.JWT_SECRET_KEY
        
    def createToken(self, user):
        # Logic to create a token
        try:
            
            payload = {
                "user_id": str(user.public_id),
                "exp": datetime.now(timezone.utc) + timedelta(seconds=self.expiry_time)
            }
            encoded_jwt = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
            return encoded_jwt
        except Exception as e:
            raise Exception(f"Error creating token: {e}")
    
    def decodeToken(self, token):
        # Logic to decode a token
        try:
            decoded_payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return decoded_payload
        except jwt.ExpiredSignatureError:
            raise Exception("Token has expired")
        except jwt.InvalidTokenError:
            raise Exception("Invalid token")
    