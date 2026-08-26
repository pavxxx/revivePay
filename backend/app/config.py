import os

class Settings:
    PROJECT_NAME: str = "RevivePay Revenue Recovery Engine"
    API_V1_STR: str = "/api"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./revivepay.db")
    
    # Razorpay credentials
    RAZORPAY_KEY_ID: str = os.getenv("RAZORPAY_KEY_ID", "rzp_test_mockkey12345")
    RAZORPAY_KEY_SECRET: str = os.getenv("RAZORPAY_KEY_SECRET", "mocksecret12345")
    USE_RAZORPAY_REAL: bool = os.getenv("USE_RAZORPAY_REAL", "false").lower() == "true"
    
    # Recovery Policy defaults
    DEFAULT_MAX_RETRIES: int = 3
    DEFAULT_PROB_FLOOR: float = 0.40
    DEFAULT_MAX_AUTO_AMOUNT: float = 50000.0  # INR 50,000 max auto-action threshold
    DEFAULT_COOLDOWN_HOURS: int = 24

settings = Settings()
