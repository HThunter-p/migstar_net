from django.contrib import admin

from accounts.admin_mixins import TenantScopedAdminMixin
from .models import Customer, AccessAccount


@admin.register(Customer)
class CustomerAdmin(TenantScopedAdminMixin, admin.ModelAdmin):
    list_display = (
        "first_name",
        "last_name",
        "phone",
        "email",
        "tenant",
        "status",
        "created_at",
    )

    list_filter = (
        "tenant",
        "status",
        "created_at",
    )

    search_fields = (
        "first_name",
        "last_name",
        "phone",
        "email",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    autocomplete_fields = (
        "tenant",
    )


@admin.register(AccessAccount)
class AccessAccountAdmin(TenantScopedAdminMixin, admin.ModelAdmin):
    list_display = (
        "username",
        "customer",
        "subscription",
        "router",
        "status",
        "provisioned_at",
        "created_at",
    )

    list_filter = (
        "tenant",
        "status",
        "router",
        "created_at",
    )

    search_fields = (
        "username",
        "customer__first_name",
        "customer__last_name",
        "customer__phone",
    )

    readonly_fields = (
        "provisioned_at",
        "last_provision_error",
        "created_at",
        "updated_at",
    )

    autocomplete_fields = (
        "tenant",
        "customer",
        "subscription",
        "router",
    )