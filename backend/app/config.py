import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "RSA CMS API")
    APP_ENV: str = os.getenv("APP_ENV", "local")
    APP_DEBUG: bool = os.getenv("APP_DEBUG", "true").lower() == "true"
    API_PREFIX: str = os.getenv("API_PREFIX", "/api")

    FRONTEND_ORIGINS: list[str] = [
        origin.strip()
        for origin in os.getenv(
            "FRONTEND_ORIGINS",
            "http://localhost:5500,http://127.0.0.1:5500,http://localhost:3000",
        ).split(",")
        if origin.strip()
    ]

    AWS_REGION: str = os.getenv("AWS_REGION", "ap-southeast-1")

    DYNAMODB_TABLE_PREFIX: str = os.getenv("DYNAMODB_TABLE_PREFIX", "rsa_cms_")
    DYNAMODB_PRODUCTS_TABLE: str = os.getenv("DYNAMODB_PRODUCTS_TABLE", "products")
    DYNAMODB_BRANDS_TABLE: str = os.getenv("DYNAMODB_BRANDS_TABLE", "brands")
    DYNAMODB_BOOKINGS_TABLE: str = os.getenv("DYNAMODB_BOOKINGS_TABLE", "bookings")
    DYNAMODB_INQUIRIES_TABLE: str = os.getenv("DYNAMODB_INQUIRIES_TABLE", "inquiries")
    DYNAMODB_CUSTOMERS_TABLE: str = os.getenv("DYNAMODB_CUSTOMERS_TABLE", "customers")

    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()