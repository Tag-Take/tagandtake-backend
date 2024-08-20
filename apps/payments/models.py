from django.db import models
from apps.members.models import MemberProfile
from apps.stores.models import StoreProfile


class MemberPaymentDetails(models.Model):
    member = models.ForeignKey(
        MemberProfile, on_delete=models.CASCADE, related_name="payment_details"
    )
    stripe_customer_id = models.CharField(max_length=255)
    stripe_account_id = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "member_payment_details"

    def __str__(self):
        return f"{self.member.name} payment details"


class StorePaymentDetails(models.Model):
    store = models.ForeignKey(
        StoreProfile, on_delete=models.CASCADE, related_name="payment_details"
    )
    stripe_customer_id = models.CharField(max_length=255)
    stripe_account_id = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "store_payment_details"

    def __str__(self):
        return f"{self.store.shop_name} payment details"
