import os
from typing import List
from  dotenv import load_dotenv

load_dotenv()
# Load environment variables
class Settings:
    def __init__(self):
        # Database
        self.DATABASE_URL = os.getenv("DATABASE_URL")
        #Redis
        self.REDIS_URL = os.getenv("REDIS_URL")

        #Stripe
        self.STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
        self.STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY")
        self.STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

        #Security
        self.DEBUG = os.getenv("DEBUG","False").lower() == "true"
        self.ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS","localhost,127.0.0.1").split(",")

def get_settings() -> Settings:
    return Settings()


# Global settings instance
settings = get_settings()


