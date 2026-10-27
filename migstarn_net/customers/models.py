from django.conf import settings
from django.db import models


class Customer(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        SUSPENDED = "SUSPENDED", "Suspended"
        INACTIVE = "INACTIVE", "Inactive"

    tenant = models.ForeignKey(
        "accounts.Tenant",
        on_delete=models.PROTECT,
        related_name="customers",
        db_index=True,
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="customer_profile",
    )

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    phone = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
    )

    email = models.EmailField(
        blank=True,
        null=True,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.phone})"
    
    
    
class AccessAccount(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        DISABLED = "DISABLED", "Disabled"
        SUSPENDED = "SUSPENDED", "Suspended"

    tenant = models.ForeignKey(
        "accounts.Tenant",
        on_delete=models.PROTECT,
        related_name="access_accounts",
        db_index=True,
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name="access_accounts",
    )

    subscription = models.OneToOneField(
        "subscriptions.Subscription",
        on_delete=models.PROTECT,
        related_name="access_account",
    )

    router = models.ForeignKey(
        "router.Router",
        on_delete=models.PROTECT,
        related_name="access_accounts",
    )

    username = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
    )

    password = models.CharField(
        max_length=255,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DISABLED,
        db_index=True,
    )

    provisioned_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    last_provision_error = models.TextField(
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

    def __str__(self):
        return f"{self.username} - {self.customer}"