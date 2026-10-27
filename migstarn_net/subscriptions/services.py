from django.utils import timezone

from .models import Subscription


class SubscriptionService:
    """
    Handles subscription lifecycle operations.
    """

    @staticmethod
    def expire_subscriptions():
        """
        Expire active subscriptions whose expiration time has passed
        and disable their associated customer access accounts.
        """

        from customers.services import AccessAccountService

        now = timezone.now()

        subscriptions = Subscription.objects.filter(
            status=Subscription.Status.ACTIVE,
            expires_at__lte=now,
        ).select_related(
            "router",
            "customer",
        )

        expired_count = 0

        for subscription in subscriptions:

            try:
                try:
                    account = subscription.access_account
                except Subscription.access_account.RelatedObjectDoesNotExist:
                    account = None

                if account and account.status == account.Status.ACTIVE:
                    AccessAccountService().disable_account(account)

                subscription.status = Subscription.Status.EXPIRED
                subscription.save(
                    update_fields=[
                        "status",
                        "updated_at",
                    ]
                )

                expired_count += 1

            except Exception as exc:

                try:
                    account = subscription.access_account
                    account.last_provision_error = str(exc)
                    account.save(
                        update_fields=[
                            "last_provision_error",
                            "updated_at",
                        ]
                    )
                except Exception:
                    pass

        return expired_count