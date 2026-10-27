from django.contrib import admin

from accounts.admin_mixins import TenantScopedAdminMixin
from .models import Plan


@admin.register(Plan)
class PlanAdmin(TenantScopedAdminMixin, admin.ModelAdmin):
    list_display = (
        "name",
        "tenant",
        "access_type",
        "price",
        "duration_value",
        "duration_unit",
        "portal_visible",
        "is_active",
        "created_at",
    )

    list_filter = (
        "tenant",
        "access_type",
        "duration_unit",
        "portal_visible",
        "is_active",
    )

    search_fields = (
        "name",
        "description",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )