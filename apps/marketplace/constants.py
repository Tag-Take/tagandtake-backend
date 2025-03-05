from django.db import models
from django.utils.translation import gettext_lazy as _

class ListingRole(models.TextChoices):
    HOST = "HOST", _("Host Store")
    OWNER = "OWNER", _("Item Owner")
    VIEWER = "VIEWER", _("Viewer")
