import firebase_admin
from firebase_admin import credentials, firestore, auth
from .config import settings

_db = None

def init_firebase():
    global _db
    if not firebase_admin._apps:
        cred = credentials.Certificate(settings.FIREBASE_SERVICE_ACCOUNT)
        firebase_admin.initialize_app(cred)
    _db = firestore.client()
    return _db

def db():
    global _db
    if _db is None:
        _db = init_firebase()
    return _db

def firebase_auth():
    return auth
