from django.db import models
from apps.stores.models import StoreProfile


class StoreSupply(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available_quantity = models.IntegerField()
    # Link to Stripe product price
    stripe_price_id = models.CharField(max_length=255, unique=True)
    
    def __str__(self):
        return self.name

class StoreSupplyPurchase(models.Model):
    store = models.ForeignKey(StoreProfile, on_delete=models.CASCADE)  
    supply = models.ForeignKey(StoreSupply, on_delete=models.CASCADE) 
    quantity = models.IntegerField(default=1) 
    purchased_at = models.DateTimeField(auto_now_add=True)  
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    # Payment-related fields
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True, null=True) 
    stripe_session_id = models.CharField(max_length=255, blank=True, null=True) 

    def __str__(self):
        return f"Purchase of {self.quantity} {self.supply.name} by {self.store.name}"
