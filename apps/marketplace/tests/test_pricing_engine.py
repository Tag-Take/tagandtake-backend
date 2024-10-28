import pytest
from apps.marketplace.services.pricing_services import PricingEngine


class TestPricingEngine:
    def test_member_and_store_pricing_add_up_to_item_price(self):
        test_prices = [10, 11.12, 43.53, 100.01, 1000.01, 234.42]
        commission = 20
        for price in test_prices:
            member_price = PricingEngine().calculate_user_earnings(price, commission)
            store_price = PricingEngine().calculate_store_commission(price, commission)
            assert round(member_price + store_price, 2) == round(price, 2)

    def test_transaction_fee_plus_item_price_equals_listing_price(self):
        test_prices = [10, 11.23, 43.53, 100.01, 1000.01, 234.42]
        for price in test_prices:
            transaction_fee = PricingEngine().calculate_transaction_fee(price)
            listing_price = PricingEngine().calculate_list_price(price)
            assert round(transaction_fee + price, 2) == round(listing_price, 2)
