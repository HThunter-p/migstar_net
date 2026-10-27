from django.contrib import admin

from accounts.admin_mixins import TenantScopedAdminMixin
from .models import Router


@admin.register(Router)
class RouterAdmin(TenantScopedAdminMixin, admin.ModelAdmin):
    list_display = (
        "name",
        "tenant",
        "host",
        "port",
        "status",
        "last_connected_at",
        "updated_at",
    )

    list_filter = (
        "tenant",
        "status",
    )

    search_fields = (
        "name",
        "host",
        "username",
    )

    readonly_fields = (
        "last_connected_at",
        "last_error",
        "created_at",
        "updated_at",
    )