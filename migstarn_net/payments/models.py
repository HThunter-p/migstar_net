import uuid

from django.db import models


class Payment(models.Model):
    class Gateway(models.TextChoices):
        LIPANA = "LIPANA", "Lipana"
        INTASEND = "INTASEND", "IntaSend"
        DARAJA = "DARAJA", "Daraja"
        PESAFLUX = "PESAFLUX", "PesaFlux"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PROCESSING = "PROCESSING", "Processing"
        SUCCESS = "SUCCESS", "Success"
        FAILED = "FAILED", "Failed"
        CANCELLED = "CANCELLED", "Cancelled"
        EXPIRED = "EXPIRED", "Expired"
        
    tenant = models.ForeignKey(
        "accounts.Tenant",
        on_delete=models.PROTECT,
        related_name="payments",
        db_index=True,
    )

    reference = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        db_index=True,
    )

    subscription = models.ForeignKey(
        "subscriptions.Subscription",
        on_delete=models.PROTECT,
        related_name="payments",
    )

    gateway = models.CharField(
        max_length=20,
        choices=Gateway.choices,
        db_index=True,
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    currency = models.CharField(
        max_length=3,
        default="KES",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )

    # Original gateway reference
    gateway_reference = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        db_index=True,
    )

    # Daraja-specific identifiers
    merchant_request_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        db_index=True,
    )

    checkout_request_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        unique=True,
    )

    mpesa_receipt_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        unique=True,
    )

    payment_url = models.URLField(
        blank=True,
        null=True,
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
    )

    gateway_response = models.JSONField(
        default=dict,
        blank=True,
    )

    failure_reason = models.TextField(
        blank=True,
    )

    paid_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-created_at"]

        indexes = [
            models.Index(
                fields=["gateway", "gateway_reference"]
            ),
            models.Index(
                fields=["subscription", "status"]
            ),
            models.Index(
                fields=["gateway", "checkout_request_id"]
            ),
        ]

    def __str__(self):
        return (
            f"{self.reference} - "
            f"{self.gateway} - "
            f"{self.amount} {self.currency} - "
            f"{self.status}"
        )