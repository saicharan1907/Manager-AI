from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import os
import bcrypt
import secrets

# Vercel Serverless needs a single static fallback signature. 
# Dynamic secrets (like token_hex) will crash validation when Vercel spins up separate lambda instances!
SECRET_KEY = os.getenv("SECRET_KEY", "manager-ai-safe-fallback-signature-123")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15  # 15 minutes

def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
