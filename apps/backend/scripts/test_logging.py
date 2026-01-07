import logging
import os
import sys

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.logging import configure_logging


def test_logging():
    configure_logging()
    logger = logging.getLogger("test")

    # 1. Test Key Masking
    print("--- Test 1: Key Masking ---")
    logger.info("User login attempt", extra={"password": "super_secret_password", "username": "test_user"})

    # 2. Test Exception PHI Masking
    print("\n--- Test 2: Exception Masking ---")
    try:
        # Simulate an error with PHI
        raise ValueError("Patient ID 12345 (John Doe, 555-0123) access denied.")
    except Exception:
        logger.exception("An error occurred processing patient data")


if __name__ == "__main__":
    test_logging()
