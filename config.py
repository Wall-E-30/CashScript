import os
from dotenv import load_dotenv

load_dotenv()
class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev_key_fallback')
    uri = os.getenv('SQLALCHEMY_DATABASE_URI')
    
    # FIX: If it starts with "postgres://", change it to "postgresql://"
    if uri and uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
        
    SQLALCHEMY_DATABASE_URI = uri or 'sqlite:///database.db'
# Mail settings
    MAIL_SERVER = 'smtp-relay.brevo.com'
    MAIL_PORT = 2525
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False

    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')

#os.environ.get()