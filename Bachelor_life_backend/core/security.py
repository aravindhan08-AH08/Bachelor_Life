import hashlib
from passlib.context import CryptContext

# pbkdf2_sha256-ai mudhalil vaithullom, yenendral ithil password length limit illai (New Account-ukku ithu help pannum)
pwd_context = CryptContext(schemes=["pbkdf2_sha256", "bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)