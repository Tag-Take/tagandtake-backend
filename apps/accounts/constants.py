from django.db import models
from django.utils.translation import gettext_lazy as _

class UserRoles(models.TextChoices):
    MEMBER = "member", _("Member")
    STORE = "store", _("Store")

