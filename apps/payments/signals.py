from django.dispatch import receiver, Signal
from django.db.models.signals import post_save
from apps.payments.models import StorePaymentDetails, MemberPaymentDetails
from apps.stores.models import StoreProfile
from apps.members.models import MemberProfile


tags_purchased = Signal()


@receiver(post_save, sender=StoreProfile)
def create_store_profile(sender, instance, **kwargs):
    StorePaymentDetails.objects.create(store=instance)


@receiver(post_save, sender=MemberProfile)
def create_member_profile(sender, instance, **kwargs):
    MemberPaymentDetails.objects.create(member=instance)


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
