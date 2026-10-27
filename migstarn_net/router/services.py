from datetime import datetime

from django.utils import timezone
from librouteros import connect

from .models import Router


class RouterConnectionError(Exception):
    """Raised when a MikroTik router connection fails."""


class RouterService:
    def __init__(self, router: Router):
        self.router = router
        self.api = None

    def connect(self):
        try:
            self.api = connect(
                username=self.router.username,
                password=self.router.password,
                host=self.router.host,
                port=self.router.port,
            )

            self.router.status = Router.Status.ACTIVE
            self.router.last_connected_at = timezone.now()
            self.router.last_error = ""
            self.router.save(
                update_fields=[
                    "status",
                    "last_connected_at",
                    "last_error",
                    "updated_at",
                ]
            )

            return self.api

        except Exception as exc:
            self.router.status = Router.Status.ERROR
            self.router.last_error = str(exc)
            self.router.save(
                update_fields=[
                    "status",
                    "last_error",
                    "updated_at",
                ]
            )

            raise RouterConnectionError(
                f"Could not connect to router '{self.router.name}': {exc}"
            ) from exc

    def disconnect(self):
        if self.api is not None:
            try:
                self.api.close()
            except Exception:
                pass
            finally:
                self.api = None

    def test_connection(self):
        api = self.connect()

        try:
            identity = list(
                api("/system/identity/print")
            )

            return identity

        finally:
            self.disconnect()
            
            
    def create_hotspot_user(
        self,
        username: str,
        password: str,
        profile: str = "default",
    ):
        api = self.connect()

        try:
            users = api.path("ip", "hotspot", "user")

            existing = [
                user
                for user in users
                if user.get("name") == username
            ]

            if existing:
                return existing[0]

            users.add(
                name=username,
                password=password,
                profile=profile,
            )

            created = [
                user
                for user in users
                if user.get("name") == username
            ]

            return created[0] if created else None

        finally:
            self.disconnect()
            
            
            
    def disable_hotspot_user(
        self,
        username: str,
    ):
        api = self.connect()

        try:
            users = api.path("ip", "hotspot", "user")

            for user in users:
                if user.get("name") == username:
                    users.update(
                        **{
                            ".id": user[".id"],
                            "disabled": "yes",
                        }
                    )
                    return user

            return None

        finally:
            self.disconnect()