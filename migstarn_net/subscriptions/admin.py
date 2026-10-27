from django.contrib import admin

from accounts.admin_mixins import TenantScopedAdminMixin
from .models import Subscription


@admin.register(Subscription)
class SubscriptionAdmin(TenantScopedAdminMixin, admin.ModelAdmin):
    list_display = (
        "reference",
        "tenant",
        "customer",
        "plan",
        "status",
        "starts_at",
        "expires_at",
        "created_at",
    )

    list_filter = (
        "tenant",
        "status",
        "plan",
        "created_at",
    )

    search_fields = (
        "reference",
        "customer__first_name",
        "customer__last_name",
        "customer__phone",
    )

    readonly_fields = (
        "reference",
        "created_at",
        "updated_at",
    )

    autocomplete_fields = (
        "tenant",
        "customer",
        "plan",
    )