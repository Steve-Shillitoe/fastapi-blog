from datetime import UTC, datetime, timedelta
import jwt
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash

from config import settings

password_hash = PasswordHash.recommended

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/users/token")