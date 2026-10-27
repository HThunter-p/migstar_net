from django.core.exceptions import PermissionDenied


class TenantScopedAdminMixin:
    """
    Restricts Django Admin records to the logged-in user's tenant.

    Root/super admins can access all tenants.
    Tenant admins can access only their own tenant's records.
    """

    tenant_field = "tenant"

    def is_root_admin(self, request):
        return request.user.is_superuser

    def get_queryset(self, request):
        queryset = super().get_queryset(request)

        if self.is_root_admin(request):
            return queryset

        tenant = request.user.tenant

        if tenant is None:
            return queryset.none()

        return queryset.filter(
            **{self.tenant_field: tenant}
        )

    def save_model(self, request, obj, form, change):
        if not self.is_root_admin(request):
            tenant = request.user.tenant

            if tenant is None:
                raise PermissionDenied(
                    "Your account is not assigned to a tenant."
                )

            setattr(obj, self.tenant_field, tenant)

        super().save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(
            super().get_readonly_fields(request, obj)
        )

        if not self.is_root_admin(request):
            if self.tenant_field not in readonly_fields:
                readonly_fields.append(self.tenant_field)

        return readonly_fields

    def formfield_for_foreignkey(
        self,
        db_field,
        request,
        **kwargs,
    ):
        if (
            not self.is_root_admin(request)
            and db_field.name != self.tenant_field
        ):
            related_model = db_field.remote_field.model

            if hasattr(related_model, "tenant"):
                tenant = request.user.tenant

                if tenant is None:
                    kwargs["queryset"] = related_model.objects.none()
                else:
                    kwargs["queryset"] = related_model.objects.filter(
                        tenant=tenant
                    )

        return super().formfield_for_foreignkey(
            db_field,
            request,
            **kwargs,
        )