import httpx

from app.core.config import settings


class PaystackService:
    def __init__(self):
        self.base_url = settings.PAYSTACK_BASE_URL
        self.secret_key = settings.PAYSTACK_SECRET_KEY

    def initialize_transaction(
        self,
        email: str,
        amount: int,
        reference: str,
    ):
        url = f"{self.base_url}/transaction/initialize"

        headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json",
        }

        data = {
            "email": email,
            "amount": amount,
            "reference": reference,

            "callback_url": ("http://127.0.0.1:5500/pages/payment_success.html"),
        }

        response = httpx.post(
            url,
            headers=headers,
            json=data,
            timeout=30.0,
        )

        response.raise_for_status()

        result = response.json()

        if not result.get("status"):
            raise ValueError(
                "Paystack transaction initialization failed."
            )

        return result["data"]

    def verify_transaction(self, reference: str):
        url = f"{self.base_url}/transaction/verify/{reference}"

        headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json",
        }

        response = httpx.get(
            url,
            headers=headers,
            timeout=30.0,
        )

        response.raise_for_status()

        result = response.json()

        if not result.get("status"):
            raise ValueError(
                "Paystack transaction verification failed."
            )

        return result["data"]