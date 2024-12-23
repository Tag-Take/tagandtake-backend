from decimal import Decimal, ROUND_HALF_UP

GRACE_PERIOD_DAYS = 7
RECALLED_LISTING_RECURRING_FEE = Decimal("5.00")


class PricingEngine:
    def __init__(self):
        self.tagandtake_commission = Decimal("0.05")
        self.tagandtake_flat_fee = Decimal("1")

    def calculate_list_price(self, price: Decimal):
        """
        Price that the buyer sees.
        """
        price = self._to_decimal(price)
        new_price = price + self.calculate_transaction_fee(price, round_result=False)
        return self._round_decimal(new_price)

    def calculate_transaction_fee(self, price: Decimal, round_result=True):
        """
        Fee that tagandtake (on top of listing price).
        """
        price = self._to_decimal(price)
        transaction_fee = (
            price * self.tagandtake_commission
        ) + self.tagandtake_flat_fee
        return self._round_decimal(transaction_fee) if round_result else transaction_fee

    def calculate_store_commission(self, price: Decimal, commission: Decimal):
        """
        Commission that the store earns.
        """
        price = self._to_decimal(price)
        commission = self._rebase_commission(commission)
        store_commission = price * commission
        return self._round_decimal(store_commission)

    def calculate_user_earnings(self, price: Decimal, commission: Decimal):
        """
        Earnings that the seller takes home.
        """
        price = self._to_decimal(price)
        commission = self._rebase_commission(commission)
        user_earnings = price - (price * commission)
        return self._round_decimal(user_earnings)

    def _to_decimal(self, value: float):
        try:
            return Decimal(str(value))
        except (ValueError, TypeError):
            raise ValueError(
                "Invalid format. Value must be a number or a string representing a number."
            )

    def _round_decimal(self, value: Decimal):
        return float(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

    def _rebase_commission(self, commission: Decimal):
        return Decimal(str(commission)) / Decimal("100")
