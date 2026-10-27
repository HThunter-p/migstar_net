from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.core.exceptions import PermissionDenied
from .models import Tenant, User


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)

        if request.user.is_superuser:
            return queryset

        tenant = request.user.tenant

        if tenant is None:
            return queryset.none()

        return queryset.filter(tenant=tenant)

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True

        if obj is None:
            return True

        return (
            obj.tenant_id == request.user.tenant_id
            and not obj.is_superuser
        )

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True

        if obj is None:
            return True

        return (
            obj.tenant_id == request.user.tenant_id
            and not obj.is_superuser
        )

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            tenant = request.user.tenant

            if tenant is None:
                raise PermissionDenied(
                    "Your account is not assigned to a tenant."
                )

            obj.tenant = tenant
            obj.is_superuser = False
            obj.is_staff = True

        super().save_model(request, obj, form, change)

    list_display = (
        "name",
        "email",
        "phone",
        "is_active",
        "created_at",
    )

    list_filter = (
        "is_active",
        "created_at",
    )

    search_fields = (
        "name",
        "email",
        "phone",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )
    
    
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    
    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)

        if request.user.is_superuser:
            return fieldsets

        restricted = []

        for name, options in fieldsets:
            fields = list(options.get("fields", ()))

            fields = [
                field
                for field in fields
                if field not in {
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                    "tenant",
                }
            ]

            restricted.append(
                (
                    name,
                    {
                        **options,
                        "fields": tuple(fields),
                    },
                )
            )

        return tuple(restricted)

    def get_add_fieldsets(self, request):
        fieldsets = super().get_add_fieldsets(request)

        if request.user.is_superuser:
            return fieldsets

        restricted = []

        for name, options in fieldsets:
            fields = list(options.get("fields", ()))

            fields = [
                field
                for field in fields
                if field != "tenant"
            ]

            restricted.append(
                (
                    name,
                    {
                        **options,
                        "fields": tuple(fields),
                    },
                )
            )

        return tuple(restricted)
    
    
    list_display = (
        "username",
        "email",
        "tenant",
        "is_staff",
        "is_superuser",
        "is_active",
    )

    list_filter = (
        "tenant",
        "is_staff",
        "is_superuser",
        "is_active",
    )

    search_fields = (
        "username",
        "email",
        "first_name",
        "last_name",
    )

    fieldsets = BaseUserAdmin.fieldsets + (
        (
            "Tenant",
            {
                "fields": ("tenant",),
            },
        ),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (
            "Tenant",
            {
                "fields": ("tenant",),
            },
        ),
    )