from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import os
import logging


class JWTHandler:
    def __init__(self):
        self.secret_key = os.getenv("JWT_SECRET_KEY", "your-secret-key")
        self.algorithm = "HS256"
        self.security = HTTPBearer()
        self.logger = logging.getLogger(__name__)

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=30)

        to_encode.update({"exp": int(expire.timestamp())})

        token = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return token

    def decode_token(self, token: str):
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            return payload

        except JWTError as e:
            self.logger.error(f"JWT Decode Error: {str(e)}")
            raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
        except Exception as e:
            self.logger.error(f"Unexpected error during token decode: {str(e)}")
            raise HTTPException(status_code=401, detail="Could not validate credentials")

    async def verify_token(self, credentials: HTTPAuthorizationCredentials = Security(HTTPBearer())):
        return self.decode_token(credentials.credentials)