from decimal import Decimal, ROUND_HALF_UP

class PricingEngine:
    def __init__(self):
        self.tagandtake_comission = Decimal('0.05')
        self.tagandtake_flat_fee = Decimal('1')

    def calculate_list_price(self, price):
        price = self._to_decimal(price)
        new_price = price + self.calculate_transaction_fee(price, round_result=False)
        return self._round_decimal(new_price)

    def calculate_transaction_fee(self, price, round_result=True):
        price = self._to_decimal(price)
        transaction_fee = (price * self.tagandtake_comission) + self.tagandtake_flat_fee
        return self._round_decimal(transaction_fee) if round_result else transaction_fee

    def calculate_store_comission(self, price, comission):
        price = self._to_decimal(price)
        comission = self._to_decimal(comission)
        store_comission = price * comission
        return self._round_decimal(store_comission)

    def calculate_user_earnings(self, price, comission):
        price = self._to_decimal(price)
        comission = self._to_decimal(comission)
        store_comission = self.calculate_store_comission(price, comission)
        user_earnings = price - store_comission
        return self._round_decimal(user_earnings)

    def _to_decimal(self, value):
        try:
            return Decimal(str(value))
        except (ValueError, TypeError):
            raise ValueError("Invalid format. Value must be a number or a string representing a number.")

    def _round_decimal(self, value):
        return float(value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))