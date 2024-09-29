from apps.payments.models.transactions import SuppliesPaymentTransaction
from apps.supplies.models import StoreSupply, SupplyCheckoutItem, SupplyOrderItem
from apps.common.constants import QUANTITY, PRICE


class SuppliesServices:

    @staticmethod
    def get_supply(price_id: str):
        try:
            return StoreSupply.objects.get(stripe_price_id=price_id)
        except StoreSupply.DoesNotExist:
            raise StoreSupply.DoesNotExist

    @staticmethod
    def create_supplies_order_items(
        transaction: SuppliesPaymentTransaction, store_id, line_items
    ):
        try:
            for item_data in line_items:
                supply = SuppliesServices.get_supply(item_data[PRICE])
                quantity = item_data[QUANTITY]

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
