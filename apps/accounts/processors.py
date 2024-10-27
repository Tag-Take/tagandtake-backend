from django.db import transaction
from django.utils.translation import gettext as _

from apps.accounts.models import User
from apps.stores.services.store_services import (
    StoreService,
)
from apps.stores.models import StoreProfile
from apps.stores.services.store_services import StoreService
from apps.members.services import MemberService
from apps.members.models import MemberProfile
from apps.common.constants import (
    USERNAME,
    EMAIL,
    PASSWORD,
    ROLE,
    STORE,
    STORE_ADDRESS,
    OPENING_HOURS,
)
from apps.common.abstract_classes import AbstractProcessor
from apps.notifications.emails.services.email_senders import AccountEmailSender


class StoreSignupProcessor(AbstractProcessor):
    def __init__(self, validated_data: dict):
        self.validated_data = validated_data
        self.store_profile_data = validated_data.pop(STORE)
        self.address_data = validated_data.pop(STORE_ADDRESS)
        self.opening_hours_data = validated_data.pop(OPENING_HOURS)

    @transaction.atomic
    def process(self):

        user = self._create_store_user()

        store_profile = self._create_store_profile(user)

        self._create_store_address(store_profile)
        self._create_store_opening_hours(store_profile)
        self._initialize_store_defaults(store_profile)

        self._send_activation_email(user)

        return user

    def _create_store_user(self):
        return User.objects.create_user(
            username=self.validated_data.get(USERNAME),
            email=self.validated_data.get(EMAIL),
            password=self.validated_data.get(PASSWORD),
            role=self.validated_data.get(ROLE),
        )

    def _create_store_profile(self, user: User):
        return StoreService.create_store_profile(user, self.store_profile_data)

    def _create_store_address(self, store_profile: StoreProfile):
        StoreService.create_store_address(store_profile, self.address_data)

    def _create_store_opening_hours(self, store_profile: StoreProfile):
        for opening_hours in self.opening_hours_data:
            StoreService.create_store_opening_hours(store_profile, opening_hours)

    def _initialize_store_defaults(self, store_profile: StoreProfile):
        StoreService.initialize_store_defaults(store_profile)

    def _send_activation_email(self, user: User):
        AccountEmailSender(user).send_activation_email()


class MemberSignupProcessor(AbstractProcessor):
    def __init__(self, validated_data: dict):
        self.validated_data = validated_data

    @transaction.atomic
    def process(self):
        user = self._create_store_user()
        member_profile = self.create_member_profile(user)
        self.initialize_store_notifications(member_profile)

        self.send_activation_email(user)

        return user

    def _create_store_user(self):
        return User.objects.create_user(
            username=self.validated_data.get(USERNAME),
            email=self.validated_data.get(EMAIL),
            password=self.validated_data.get(PASSWORD),
            role=self.validated_data.get(ROLE),
        )

    @staticmethod
    def create_member_profile(user):
        return MemberService.create_member_profile(user)

    @staticmethod
    def initialize_store_notifications(member: MemberProfile):
        MemberService.initialize_store_notifications(member)

    @staticmethod
    def send_activation_email(user: User):
        AccountEmailSender(user).send_activation_email()
