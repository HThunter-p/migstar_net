from .models import Router
from .services import RouterService


class ProvisioningService:
    """
    Handles customer access provisioning on MikroTik routers.
    """

    def __init__(self, router: Router):
        self.router = router
        self.router_service = RouterService(router)

    def provision_user(
        self,
        username: str,
        password: str,
        profile: str = "default",
    ):
        """
        Create or retrieve a MikroTik Hotspot user.
        """
        return self.router_service.create_hotspot_user(
            username=username,
            password=password,
            profile=profile,
        )
        
    def disable_user(self, username: str):
        return self.router_service.disable_hotspot_user(
            username=username,
        )