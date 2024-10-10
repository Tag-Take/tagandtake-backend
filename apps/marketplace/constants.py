from django.db import models
from django.utils.translation import gettext_lazy as _


class ListingRole(models.TextChoices):
    HOST_STORE = "HOST_STORE", _("Host Store")
    ITEM_OWNER = "ITEM_OWNER", _("Item Owner")
    GUEST = "GUEST", _("Guest")
