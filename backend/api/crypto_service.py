# api/crypto_service.py
from cryptography.fernet import Fernet
import os

# Recommended: set key in env var for persistence across restarts:
# export FERNET_KEY="..."  (on Windows: setx FERNET_KEY "...")
FERNET_KEY = os.environ.get('FERNET_KEY')
if not FERNET_KEY:
    # For development only — generate a key if none provided
    FERNET_KEY = Fernet.generate_key().decode()

fernet = Fernet(FERNET_KEY.encode())

class MessageService:
    def encrypt(self, plaintext: str) -> str:
        return fernet.encrypt(plaintext.encode()).decode()

    def decrypt(self, token: str) -> str:
        return fernet.decrypt(token.encode()).decode()

message_service = MessageService()
