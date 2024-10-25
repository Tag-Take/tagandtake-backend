from django.contrib import admin

from apps.stores.models import (
    StoreProfile,
    StoreItemCategory,
    StoreItemCondition,
    StoreNotificationPreferences,
    TagGroup,
    Tag,
)

admin.site.register(StoreProfile)
admin.site.register(StoreItemCategory)
admin.site.register(StoreItemCondition)
admin.site.register(StoreNotificationPreferences)
admin.site.register(TagGroup)
admin.site.register(Tag)
