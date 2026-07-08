import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth

cred = credentials.Certificate(
    "ai-nano-counter-87b7c-firebase-adminsdk-fbsvc-8e93e9f55b.json"
)

try:
    firebase_admin.get_app()
except ValueError:
    firebase_admin.initialize_app(cred)


def verify_token(id_token):
    return auth.verify_id_token(id_token)