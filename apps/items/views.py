from apps.members.permissions import IsMemberUser
from apps.items.serializers import (
    ItemSerializer,
    ItemCategorySerializer,
    ItemConditionSerializer,
)

# All the views needed for users in the marketplace to manage their items (CRUD)

# Create a new item
# POST /api/items/

# Get all items from a user
# GET /api/items/member/<int:user_id>/

# Get all items from a store
# GET /api/items/store/<int:store_id>/

# Get a single item
# GET /api/items/<int:item_id>/

# Update an item
# PUT /api/items/<int:item_id>/

# Delete an item
# DELETE /api/items/<int:item_id>/

# Get all item categories
# GET /api/items/categories/

# Get all item conditions
# GET /api/items/conditions/
