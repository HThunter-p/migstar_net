
from .base import (
    PaymentGateway,
    PaymentRequest,
    PaymentResult,
)


class LipanaGateway(PaymentGateway):
    """
    Lipana payment gateway adapter.

    The actual Lipana API implementation will be added later.
    """

    def initiate(
        self,
        request: PaymentRequest,
    ) -> PaymentResult:

        raise NotImplementedError(
            "Lipana payment integration has not been implemented yet."
        )

    def check_status(
        self,
        gateway_reference: str,
    ) -> PaymentResult:

        raise NotImplementedError(
            "Lipana payment status checking has not been implemented yet."
        )

    def verify_webhook(
        self,
        payload: bytes,
        headers: dict[str, str],
    ) -> bool:

        raise NotImplementedError(
            "Lipana webhook verification has not been implemented yet."
        )

