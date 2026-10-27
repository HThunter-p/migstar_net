from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Custom user model for Migstar N-Net.

    Root administrators have no tenant.
    Tenant administrators belong to one tenant.
    """

    tenant = models.ForeignKey(
        "Tenant",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
    )

    def __str__(self):
        return self.username

class Tenant(models.Model):
    """
    Represents a business/operator that owns and manages
    its own WiFi billing resources.
    """
    
    class BusinessModel(models.TextChoices):
        PURCHASED = "PURCHASED", "Purchased"
        COMMISSIONED = "COMMISSIONED", "Commissioned"
        
    name = models.CharField(
        max_length=150,
        unique=True,
    )
    
    
    business_model = models.CharField(
        max_length=20,
        choices=BusinessModel.choices,
        default=BusinessModel.PURCHASED,
        db_index=True,
    )
    

    email = models.EmailField(
        blank=True,
        null=True,
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
    )

    address = models.CharField(
        max_length=255,
        blank=True,
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
        ordering = ["name"]

    def __str__(self):
        return self.name