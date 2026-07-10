import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth

cred_path = os.getenv(
    "GOOGLE_APPLICATION_CREDENTIALS",
    "firebase-admin.json"
)

cred = credentials.Certificate(cred_path)

try:
    firebase_admin.get_app()
except ValueError:
    firebase_admin.initialize_app(cred)


def verify_token(id_token):
    return auth.verify_id_token(id_token)