from django.db import models


class Plan(models.Model):

    class AccessType(models.TextChoices):
        PAID = "PAID", "Paid"
        AD_SUPPORTED = "AD_SUPPORTED", "Ad-Supported"
        MAC = "MAC", "MAC Address"

    class DurationUnit(models.TextChoices):
        HOUR = "HOUR", "Hour"
        DAY = "DAY", "Day"
        WEEK = "WEEK", "Week"
        MONTH = "MONTH", "Month"
        
    tenant = models.ForeignKey(
        "accounts.Tenant",
        on_delete=models.PROTECT,
        related_name="plans",
        db_index=True,
    )

    name = models.CharField(
        max_length=100,
    )

    description = models.TextField(
        blank=True,
    )

    access_type = models.CharField(
        max_length=20,
        choices=AccessType.choices,
        default=AccessType.PAID,
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    duration_value = models.PositiveIntegerField(
        default=1,
    )

    duration_unit = models.CharField(
        max_length=10,
        choices=DurationUnit.choices,
        default=DurationUnit.DAY,
    )

    router_profile = models.CharField(
        max_length=100,
        blank=True,
        help_text="MikroTik hotspot/PPP profile associated with this plan.",
    )

    unlimited_data = models.BooleanField(
        default=True,
    )

    data_limit_mb = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        help_text="Data allowance in MB. Leave empty for unlimited data.",
    )

    download_speed_mbps = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    upload_speed_mbps = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    portal_visible = models.BooleanField(
        default=True,
        help_text="Whether this plan can appear on the captive portal.",
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["price", "duration_value"]

    def __str__(self):
        return f"{self.name} - KSh {self.price}"