
from .base import (
    PaymentGateway,
    PaymentRequest,
    PaymentResult,
)


class IntaSendGateway(PaymentGateway):
    """
    IntaSend payment gateway adapter.

    The actual IntaSend API implementation will be added later.
    """

    def initiate(
        self,
        request: PaymentRequest,
    ) -> PaymentResult:

        raise NotImplementedError(
            "IntaSend payment integration has not been implemented yet."
        )

    def check_status(
        self,
        gateway_reference: str,
    ) -> PaymentResult:

        raise NotImplementedError(
            "IntaSend payment status checking has not been implemented yet."
        )

    def verify_webhook(
        self,
        payload: bytes,
        headers: dict[str, str],
    ) -> bool:

        raise NotImplementedError(
            "IntaSend webhook verification has not been implemented yet."
        )

