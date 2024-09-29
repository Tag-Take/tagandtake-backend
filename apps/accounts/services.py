import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class UsernameValidatorService:
    def __init__(self, min_length: int = 3, max_length: int = 30):
        self.min_length = min_length
        self.max_length = max_length
        self.username_regex = re.compile(r"^[a-z0-9_]+$")

    def __call__(self, username: str):
        if len(username) <= self.min_length or len(username) >= self.max_length:
            raise ValidationError(
                _(
                    f"Username must be at least {self.min_length}, and no longer than {self.max_length} characters."
                ),
                code="invalid_length",
            )

        if not self.username_regex.match(username):
            raise ValidationError(
                _(
                    "Username can only contain lowercase letters, numbers, and underscores."
                ),
                code="invalid_characters",
            )

        reserved_usernames = ["admin", "root", "system"]
        if username.lower() in reserved_usernames:
            raise ValidationError(
                _(f"The username '{username}' is reserved and cannot be used."),
                code="reserved_username",
            )
