from django.contrib import admin

from accounts.admin_mixins import TenantScopedAdminMixin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(TenantScopedAdminMixin, admin.ModelAdmin):
    list_display = (
        "reference",
        "tenant",
        "subscription",
        "gateway",
        "amount",
        "currency",
        "status",
        "gateway_reference",
        "paid_at",
        "created_at",
    )

    list_filter = (
        "tenant",
        "gateway",
        "status",
        "currency",
        "created_at",
    )

    search_fields = (
        "reference",
        "gateway_reference",
        "subscription__reference",
        "subscription__customer__phone",
        "subscription__customer__first_name",
        "subscription__customer__last_name",
    )

    readonly_fields = (
        "reference",
        "gateway_response",
        "paid_at",
        "created_at",
        "updated_at",
    )

    autocomplete_fields = (
        "tenant",
        "subscription",
    )