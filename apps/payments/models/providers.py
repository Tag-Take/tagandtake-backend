from django.db import models


class PaymentProvider(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    api_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} (Payment Provider)"

    class Meta:
        verbose_name = "Payment Provider"
        verbose_name_plural = "Payment Providers"
        db_table = "payment_providers"


class PayoutProvider(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    api_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} (Payout Provider)"

    class Meta:
        verbose_name = "Payout Provider"
        verbose_name_plural = "Payout Providers"
        db_table = "payout_providers"
