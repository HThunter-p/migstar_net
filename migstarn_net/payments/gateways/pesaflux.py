
from .base import (
    PaymentGateway,
    PaymentRequest,
    PaymentResult,
)


class PesaFluxGateway(PaymentGateway):
    """
    PesaFlux payment gateway adapter.

    The actual PesaFlux API implementation will be added later.
    """

    def initiate(
        self,
        request: PaymentRequest,
    ) -> PaymentResult:

        raise NotImplementedError(
            "PesaFlux payment integration has not been implemented yet."
        )

    def check_status(
        self,
        gateway_reference: str,
    ) -> PaymentResult:

        raise NotImplementedError(
            "PesaFlux payment status checking has not been implemented yet."
        )

    def verify_webhook(
        self,
        payload: bytes,
        headers: dict[str, str],
    ) -> bool:

        raise NotImplementedError(
            "PesaFlux webhook verification has not been implemented yet."
        )
