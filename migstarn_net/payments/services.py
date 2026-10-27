from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from .gateways.base import PaymentRequest
from .gateways.factory import PaymentGatewayFactory
from .models import Payment


class PaymentService:
    """
    Central payment service.

    Application code should use this service instead of
    communicating directly with payment providers.
    """

    @staticmethod
    @transaction.atomic
    def create_payment(
        subscription,
        phone,
    ) -> Payment:
        """
        Create a pending payment for a subscription.
        """

        if subscription.status != subscription.Status.PENDING:
            raise ValueError(
                "Payment can only be created for a pending subscription."
            )

        plan = subscription.plan

        selected_gateway = settings.PAYMENT_GATEWAY

        payment = Payment.objects.create(
            tenant=subscription.tenant,
            subscription=subscription,
            gateway=selected_gateway,
            amount=plan.price,
            currency="KES",
            phone=phone,
            status=Payment.Status.PENDING,
        )

        return payment
    
    
    @staticmethod
    @transaction.atomic
    def confirm_payment(
        payment: Payment,
    ) -> Payment:
        """
        Confirm a successful payment, activate the subscription,
        and provision customer access.

        The operation is designed to be safe for repeated callbacks.
        """

        from customers.services import AccessAccountService

        subscription = payment.subscription

        # A payment already marked SUCCESS has already completed
        # the payment portion of the process.
        if payment.status == Payment.Status.SUCCESS:
            return payment

        # A payment must be explicitly processing before confirmation.
        if payment.status != Payment.Status.PROCESSING:
            raise ValueError(
                "Only a processing payment can be confirmed."
            )

        now = timezone.now()

        payment.status = Payment.Status.SUCCESS
        payment.paid_at = now
        payment.failure_reason = ""

        payment.save(
            update_fields=[
                "status",
                "paid_at",
                "failure_reason",
                "updated_at",
            ]
        )

        # Activate the subscription if it is not already active.
        if subscription.status != subscription.Status.ACTIVE:

            plan = subscription.plan

            subscription.starts_at = now

            if plan.duration_unit == "HOUR":
                subscription.expires_at = (
                    now + timedelta(
                        hours=plan.duration_value
                    )
                )

            elif plan.duration_unit == "DAY":
                subscription.expires_at = (
                    now + timedelta(
                        days=plan.duration_value
                    )
                )

            elif plan.duration_unit == "WEEK":
                subscription.expires_at = (
                    now + timedelta(
                        weeks=plan.duration_value
                    )
                )

            elif plan.duration_unit == "MONTH":
                # Temporary month approximation.
                # Replace with proper calendar month handling
                # before production.
                subscription.expires_at = (
                    now + timedelta(
                        days=30 * plan.duration_value
                    )
                )

            else:
                raise ValueError(
                    f"Unsupported duration unit: "
                    f"{plan.duration_unit}"
                )

            subscription.status = subscription.Status.ACTIVE

            subscription.save(
                update_fields=[
                    "status",
                    "starts_at",
                    "expires_at",
                    "updated_at",
                ]
            )

        # Create the access account if necessary.
        account_service = AccessAccountService()

        account, created = account_service.create_account(
            subscription=subscription,
            username=f"customer_{subscription.id}",
            password=str(subscription.reference)[:12],
        )

        # Provision only when the account is not already active.
        if account.status != account.Status.ACTIVE:
            account_service.provision_account(account)

        return payment


    @staticmethod
    @transaction.atomic
    def initiate_payment(payment: Payment) -> Payment:

        gateway = PaymentGatewayFactory.create(
            payment.gateway
        )

        customer = payment.subscription.customer

        request = PaymentRequest(
            reference=str(payment.reference),
            amount=payment.amount,
            currency=payment.currency,
            phone=payment.phone,
            customer_name=(
                f"{customer.first_name} "
                f"{customer.last_name}"
            ),
            customer_email=customer.email,
            description=(
                f"{payment.subscription.plan.name} "
                f"subscription"
            ),
        )

        payment.status = Payment.Status.PROCESSING

        payment.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        result = gateway.initiate(request)

        if result.gateway_reference:
            payment.gateway_reference = result.gateway_reference

            if payment.gateway == Payment.Gateway.DARAJA:
                payment.checkout_request_id = result.gateway_reference

        if result.payment_url:
            payment.payment_url = result.payment_url

        if result.raw_response:
            payment.gateway_response = (
                result.raw_response
            )

        if result.success:
            if result.status == "SUCCESS":
                payment.status = Payment.Status.SUCCESS
            else:
                payment.status = Payment.Status.PROCESSING
        else:
            payment.status = Payment.Status.FAILED
            payment.failure_reason = result.message

        payment.save(
            update_fields=[
                "status",
                "gateway_reference",
                "checkout_request_id",
                "payment_url",
                "gateway_response",
                "failure_reason",
                "updated_at",
            ]
        )
        return payment
    
    
    @staticmethod
    def check_payment_status(payment: Payment) -> Payment:
        """
        Ask the configured gateway for the latest payment status.
        """

        if payment.status in (
            Payment.Status.SUCCESS,
            Payment.Status.FAILED,
            Payment.Status.CANCELLED,
            Payment.Status.EXPIRED,
        ):
            return payment

        if not payment.gateway_reference:
            raise ValueError(
                "Payment does not have a gateway reference."
            )

        gateway = PaymentGatewayFactory.create(
            payment.gateway
        )

        result = gateway.check_status(
            payment.gateway_reference
        )

        if result.raw_response:
            payment.gateway_response = result.raw_response
            payment.save(
                update_fields=[
                    "gateway_response",
                    "updated_at",
                ]
            )

        return payment
    

    
    
    
    @staticmethod
    @transaction.atomic
    def process_daraja_callback(payload: dict) -> Payment | None:
        """
        Process a Safaricom Daraja STK Push callback.

        Finds the payment using CheckoutRequestID,
        stores the complete gateway response, and
        confirms successful payments.
        """

        body = payload.get("Body", {})
        callback = body.get("stkCallback", {})

        checkout_request_id = callback.get(
            "CheckoutRequestID"
        )

        merchant_request_id = callback.get(
            "MerchantRequestID"
        )

        result_code = callback.get("ResultCode")
        result_desc = callback.get("ResultDesc", "")

        if not checkout_request_id:
            raise ValueError(
                "Daraja callback missing CheckoutRequestID."
            )

        try:
            payment = Payment.objects.select_for_update().get(
                checkout_request_id=checkout_request_id
            )
        except Payment.DoesNotExist:
            return None

        # Store the complete callback response.
        payment.gateway_response = payload
        payment.merchant_request_id = merchant_request_id

        # Successful payment.
        if result_code == 0:
            callback_metadata = callback.get(
                "CallbackMetadata",
                {},
            )

            items = callback_metadata.get(
                "Item",
                [],
            )

            metadata = {}

            for item in items:
                name = item.get("Name")
                value = item.get("Value")

                if name:
                    metadata[name] = value

            payment.mpesa_receipt_number = metadata.get(
                "MpesaReceiptNumber"
            )

            if metadata.get("PhoneNumber"):
                payment.phone = str(
                    metadata["PhoneNumber"]
                )

            PaymentService.confirm_payment(payment)

            payment.gateway_response = payload
            payment.merchant_request_id = (
                merchant_request_id
            )

            payment.save(
                update_fields=[
                    "gateway_response",
                    "merchant_request_id",
                    "mpesa_receipt_number",
                    "phone",
                    "updated_at",
                ]
            )

        else:
            payment.status = Payment.Status.FAILED
            payment.failure_reason = result_desc
            payment.gateway_response = payload
            payment.merchant_request_id = (
                merchant_request_id
            )

            payment.save(
                update_fields=[
                    "status",
                    "failure_reason",
                    "gateway_response",
                    "merchant_request_id",
                    "updated_at",
                ]
            )

        return payment
    