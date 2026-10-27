from django.conf import settings

from .base import PaymentGateway


class PaymentGatewayFactory:

    @staticmethod
    def create(
        gateway_name: str | None = None,
    ) -> PaymentGateway:

        gateway_name = (
            gateway_name
            or getattr(
                settings,
                "PAYMENT_GATEWAY",
                "DARAJA",
            )
        ).upper()

        if gateway_name == "DARAJA":
            from .daraja import DarajaGateway

            return DarajaGateway()

        if gateway_name == "LIPANA":
            from .lipana import LipanaGateway

            return LipanaGateway()

        if gateway_name == "INTASEND":
            from .intasend import IntaSendGateway

            return IntaSendGateway()

        if gateway_name == "PESAFLUX":
            from .pesaflux import PesaFluxGateway

            return PesaFluxGateway()

        raise ValueError(
            f"Unsupported payment gateway: {gateway_name}"
        )