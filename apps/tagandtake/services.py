from apps.payments.models.transactions import SuppliesPaymentTransaction
from apps.tagandtake.models import StoreSupply, SupplyCheckoutItem, SupplyOrderItem
from apps.payments.utils import from_stripe_amount


class SuppliesHandler:
    def purchase_supplies(transaction, store_id, line_items):
        try:
            for item_data in line_items:
                supply = StoreSupply.objects.get(stripe_price_id=item_data["price"])
                quantity = item_data["quantity"]

                SupplyOrderItem.objects.create(
                    order=transaction,
                    store=store_id,
                    supply=supply,
                    quantity=quantity,
                    item_price=supply.price,
                    total_price=transaction.amount,
                )

        except Exception as e:
            raise e

    def save_supplies_checkout_session(supplies_checkout_session, store, line_items):
        try:
            for item_data in line_items:
                supply = StoreSupply.objects.get(stripe_price_id=item_data["price"])
                quantity = item_data["quantity"]

                SupplyCheckoutItem.objects.create(
                    checkout_session=supplies_checkout_session,
                    supply=supply,
                    store=store,
                    quantity=quantity,
                    item_price=supply.price,
                )
        except Exception as e:
            raise e
