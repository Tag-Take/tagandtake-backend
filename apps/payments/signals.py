from django.dispatch import receiver
from django.db.models.signals import post_save
from apps.payments.models import StorePaymentDetails, MemberPaymentDetails
from apps.stores.models import StoreProfile
from apps.members.models import MemberProfile


@receiver(post_save, sender=StoreProfile)
def create_store_profile(sender, instance, **kwargs):
    if instance.is_active and instance.role == "store":
        store_profile, created = StoreProfile.objects.get_or_create(user=instance)
        if created:
            StorePaymentDetails.objects.create(store=store_profile)


@receiver(post_save, sender=MemberProfile)
def create_member_profile(sender, instance, **kwargs):
    if instance.is_active and instance.role == "member":
        member_profile, created = MemberProfile.objects.get_or_create(user=instance)
        if created:
            MemberPaymentDetails.objects.create(member=member_profile)


#  TODO: create stripe account for store
# @receiver(post_save, sender=StorePaymentDetails)
# def create_strpie_connect_account(sender, instance, created, **kwargs):
#     if created:
#         try:
#             stripe_account_id = create_stripe_connected_account(instance.user.email)
#             instance.stripe_account_id = stripe_account_id
#             instance.save()
#         except Exception as e:
#             # Handle error, maybe log it or notify admin
#             pass

# TODO: create stripe account for member
# @receiver(post_save, sender=MemberPaymentDetails)
# def create_strpie_connect_account(sender, instance, created, **kwargs):
#     if created:
#         try:
#             stripe_account_id = create_stripe_connected_account(instance.user.email)
#             instance.stripe_account_id = stripe_account_id
#             instance.save()
#         except Exception as e:
#             # Handle error, maybe log it or notify admin
#             pass
