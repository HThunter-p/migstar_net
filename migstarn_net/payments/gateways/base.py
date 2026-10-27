
from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from typing import Any


@dataclass
class PaymentRequest:
    """
    Standard payment request used internally by Migstar N-Net.

    Individual gateways translate this request into
    their own API format.
    """

    reference: str
    amount: Decimal
    currency: str
    phone: str
    customer_name: str
    customer_email: str | None = None
    description: str = ""


@dataclass
class PaymentResult:
    """
    Standard response returned by every payment gateway.
    """

    success: bool
    status: str
    gateway_reference: str | None = None
    payment_url: str | None = None
    message: str = ""
    raw_response: dict[str, Any] | None = None


class PaymentGateway(ABC):
    """
    Common interface implemented by every payment provider.
    """

    @abstractmethod
    def initiate(self, request: PaymentRequest) -> PaymentResult:
        """
        Initiate a payment.
        """
        raise NotImplementedError

    @abstractmethod
    def check_status(self, gateway_reference: str) -> PaymentResult:
        """
        Check the current status of a gateway transaction.
        """
        raise NotImplementedError

    @abstractmethod
    def verify_webhook(
        self,
        payload: bytes,
        headers: dict[str, str],
    ) -> bool:
        """
        Verify that a webhook genuinely came from the gateway.
        """
        raise NotImplementedError

