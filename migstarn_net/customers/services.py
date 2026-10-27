from django.utils import timezone

from .models import AccessAccount
from router.provisioning import ProvisioningService


class AccessAccountService:
    """
    Handles creation and management of customer access accounts.
    """

    def create_account(
        self,
        subscription,
        username,
        password,
    ):
        """
        Create or return the AccessAccount for an active subscription.
        """

        if subscription.status != subscription.Status.ACTIVE:
            raise ValueError(
                "AccessAccount can only be created for an active subscription."
            )

        if subscription.router is None:
            raise ValueError(
                "Subscription must have a router assigned."
            )

        account, created = AccessAccount.objects.get_or_create(
            subscription=subscription,
            defaults={
                "tenant": subscription.tenant,
                "customer": subscription.customer,
                "router": subscription.router,
                "username": username,
                "password": password,
                "status": AccessAccount.Status.DISABLED,
                "provisioned_at": None,
                "last_provision_error": "",
            },
        )

        return account, created

    def provision_account(self, account):
        """
        Provision an AccessAccount on its MikroTik router.
        """

        try:
            provisioning = ProvisioningService(account.router)

            provisioning.provision_user(
                username=account.username,
                password=account.password,
                profile=account.subscription.plan.router_profile or "default",
            )

            account.status = AccessAccount.Status.ACTIVE
            account.provisioned_at = timezone.now()
            account.last_provision_error = ""
            account.save(
                update_fields=[
                    "status",
                    "provisioned_at",
                    "last_provision_error",
                    "updated_at",
                ]
            )

            return account

        except Exception as exc:
            account.status = AccessAccount.Status.DISABLED
            account.last_provision_error = str(exc)
            account.save(
                update_fields=[
                    "status",
                    "last_provision_error",
                    "updated_at",
                ]
            )

            raise
        
        
        
    def disable_account(self, account):
        """
        Disable an AccessAccount on its MikroTik router.
        """

        try:
            provisioning = ProvisioningService(account.router)

            provisioning.disable_user(
                username=account.username,
            )

            account.status = AccessAccount.Status.DISABLED
            account.last_provision_error = ""
            account.save(
                update_fields=[
                    "status",
                    "last_provision_error",
                    "updated_at",
                ]
            )

            return account

        except Exception as exc:
            account.last_provision_error = str(exc)
            account.save(
                update_fields=[
                    "last_provision_error",
                    "updated_at",
                ]
            )

            raise