import base64
from datetime import datetime
from typing import Any

import requests
from django.conf import settings

from .base import (
    PaymentGateway,
    PaymentRequest,
    PaymentResult,
)


class DarajaGateway(PaymentGateway):
    SANDBOX_BASE_URL = "https://sandbox.safaricom.co.ke"
    PRODUCTION_BASE_URL = "https://api.safaricom.co.ke"

    def __init__(self):
        self.consumer_key = settings.DARAJA_CONSUMER_KEY
        self.consumer_secret = settings.DARAJA_CONSUMER_SECRET
        self.shortcode = settings.DARAJA_SHORTCODE
        self.passkey = settings.DARAJA_PASSKEY
        self.callback_url = settings.DARAJA_CALLBACK_URL

        environment = getattr(
            settings,
            "DARAJA_ENVIRONMENT",
            "sandbox",
        ).lower()

        self.base_url = (
            self.PRODUCTION_BASE_URL
            if environment == "production"
            else self.SANDBOX_BASE_URL
        )

    # ---------------------------------------------------------
    # OAuth
    # ---------------------------------------------------------

    def _get_access_token(self) -> str:
        if not self.consumer_key:
            raise ValueError(
                "DARAJA_CONSUMER_KEY is not configured."
            )

        if not self.consumer_secret:
            raise ValueError(
                "DARAJA_CONSUMER_SECRET is not configured."
            )

        credentials = (
            f"{self.consumer_key}:{self.consumer_secret}"
        )

        encoded_credentials = base64.b64encode(
            credentials.encode("utf-8")
        ).decode("utf-8")

        response = requests.get(
            (
                f"{self.base_url}"
                "/oauth/v1/generate"
                "?grant_type=client_credentials"
            ),
            headers={
                "Authorization": (
                    f"Basic {encoded_credentials}"
                ),
                "Content-Type": "application/json",
            },
            timeout=30,
        )

        response.raise_for_status()

        data = response.json()

        access_token = data.get("access_token")

        if not access_token:
            raise ValueError(
                "Daraja did not return an access token."
            )

        return access_token

    # ---------------------------------------------------------
    # STK Push Password
    # ---------------------------------------------------------

    def _generate_password(
        self,
        timestamp: str,
    ) -> str:

        if not self.shortcode:
            raise ValueError(
                "DARAJA_SHORTCODE is not configured."
            )

        if not self.passkey:
            raise ValueError(
                "DARAJA_PASSKEY is not configured."
            )

        raw_password = (
            f"{self.shortcode}"
            f"{self.passkey}"
            f"{timestamp}"
        )

        return base64.b64encode(
            raw_password.encode("utf-8")
        ).decode("utf-8")

    # ---------------------------------------------------------
    # Phone normalization
    # ---------------------------------------------------------

    @staticmethod
    def _normalize_phone(phone: str) -> str:
        phone = (
            str(phone)
            .strip()
            .replace(" ", "")
        )

        if phone.startswith("+254"):
            phone = phone[1:]

        elif phone.startswith("07"):
            phone = "254" + phone[1:]

        elif phone.startswith("01"):
            phone = "254" + phone[1:]

        if (
            not phone.startswith("254")
            or len(phone) != 12
            or not phone.isdigit()
        ):
            raise ValueError(
                "Invalid Kenyan phone number. "
                "Use 2547XXXXXXXX or 2541XXXXXXXX."
            )

        return phone

    # ---------------------------------------------------------
    # STK Push
    # ---------------------------------------------------------

    def initiate(
        self,
        request: PaymentRequest,
    ) -> PaymentResult:

        try:
            access_token = self._get_access_token()

            phone = self._normalize_phone(
                request.phone
            )

            timestamp = datetime.now().strftime(
                "%Y%m%d%H%M%S"
            )

            password = self._generate_password(
                timestamp
            )

            amount = int(request.amount)

            payload = {
                "BusinessShortCode": self.shortcode,
                "Password": password,
                "Timestamp": timestamp,
                "TransactionType": (
                    "CustomerPayBillOnline"
                ),
                "Amount": amount,
                "PartyA": phone,
                "PartyB": self.shortcode,
                "PhoneNumber": phone,
                "CallBackURL": self.callback_url,
                "AccountReference": (
                    request.reference[:20]
                ),
                "TransactionDesc": (
                    request.description[:20]
                    or "MIGSTAR N-NET"
                ),
            }

            response = requests.post(
                (
                    f"{self.base_url}"
                    "/mpesa/stkpush/v1/processrequest"
                ),
                headers={
                    "Authorization": (
                        f"Bearer {access_token}"
                    ),
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=30,
            )

            data: dict[str, Any] = response.json()

            if (
                response.ok
                and data.get("ResponseCode") == "0"
            ):
                return PaymentResult(
                    success=True,
                    status="PROCESSING",
                    gateway_reference=data.get(
                        "CheckoutRequestID"
                    ),
                    message=data.get(
                        "CustomerMessage",
                        "STK Push sent successfully.",
                    ),
                    raw_response=data,
                )

            return PaymentResult(
                success=False,
                status="FAILED",
                gateway_reference=data.get(
                    "CheckoutRequestID"
                ),
                message=data.get(
                    "errorMessage"
                    or data.get(
                        "ResponseDescription",
                        "Daraja STK Push failed.",
                    )
                ),
                raw_response=data,
            )

        except requests.RequestException as exc:
            return PaymentResult(
                success=False,
                status="FAILED",
                message=(
                    f"Daraja connection error: {exc}"
                ),
                raw_response={},
            )

        except Exception as exc:
            return PaymentResult(
                success=False,
                status="FAILED",
                message=str(exc),
                raw_response={},
            )

    # ---------------------------------------------------------
    # Transaction Status
    # ---------------------------------------------------------

    def check_status(
        self,
        gateway_reference: str,
    ) -> PaymentResult:

        raise NotImplementedError(
            "Daraja Transaction Status will be "
            "implemented after the STK Push flow "
            "is fully verified."
        )

    # ---------------------------------------------------------
    # Webhook verification
    # ---------------------------------------------------------

    def verify_webhook(
        self,
        payload: bytes,
        headers: dict[str, str],
    ) -> bool:

        # Temporary implementation.
        # This will be hardened before production.
        return True