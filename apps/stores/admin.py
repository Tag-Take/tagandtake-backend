from django.contrib import admin

from apps.stores.models import (
    StoreProfile,
    StoreItemCategorie,
    StoreItemConditions,
    StoreNotificationPreferences,
    TagGroup,
    Tag,
)

admin.site.register(StoreProfile)
admin.site.register(StoreItemCategorie)
admin.site.register(StoreItemConditions)
admin.site.register(StoreNotificationPreferences)
admin.site.register(TagGroup)
admin.site.register(Tag)