"""
NOTE: The constants below, although grouped (for readability),
      are not used solely within the apps they are grouped by.
"""

# COMMON
NAME: str = "name"
EMAIL: str = "email"
PIN: str = "pin"
ID: str = "id"
UID: str = "uid"
TOKEN: str = "token"
ACCESS: str = "access"
ACCESS_TOKEN: str = "access_token"
REFRESH: str = "refresh"
REFRESH_TOKEN: str = "refresh_token"
SKIP_AUTHENTICATION: str = "skip_authentication"
CONFIRM: str = "confirm"
STATUS: str = "status"
DATA: str = "data"
MESSAGE: str = "message"
SUCCESS: str = "success"
ERROR: str = "error"
ERRORS: str = "errors"
IMAGES: str = "images"
PROFILES: str = "profiles"
S3: str = "s3"
KEY: str = "Key"
FIELDS: str = "fields"
IMAGE = "image"
IMAGES = "images"
REQUEST: str = "request"
CREATED_AT: str = "created_at"
UPDATED_AT: str = "updated_at"
TYPE: str = "type"
CODE: str = "code"
OBJECT: str = "object"
ACCOUNT: str = "account"

# ACCOUNTS
USER: str = "user"
USER_ID: str = "user_id"
ROLE: str = "role"
USERNAME: str = "username"
PASSWORD: str = "password"
PASSWORD2: str = "password2"
IS_ACTIVE: str = "is_active"
IS_STAFF: str = "is_staff"
IS_SUPERUSER: str = "is_superuser"
CUSTOM_USER_SET: str = "custom_user_set"
NEW_PASSWORD: str = "new_password"
CONFIRM_NEW_PASSWORD: str = "confirm_new_password"
SIGNUP: str = "signup"
LOGIN: str = "login"
ACTIVATE: str = "activate"
RESEND_ACTIVATION: str = "resend_activation"
PASSWORD_RESET: str = "password_reset"

# ITEMS
ITEM: str = "item"
ITEMS: str = "items"
ITEM_ID: str = "item_id"
ITEM_NAME: str = "item_name"
ITEM_IMAGE: str = "item_image"
CONDITION: str = "condition"
CATEGORY: str = "category"
DESCRIPTION: str = "description"
ORDER: str = "order"
IMAGE_URL: str = "image_url"
SIZE: str = "size"
BRAND: str = "brand"
PRICE: str = "price"
CATEGORY_DETAILS: str = "category_details"
CONDITION_DETAILS: str = "condition_details"
MAIN_IMAGE: str = "main_image"
CATEGORIES: str = "categories"
CONDITIONS: str = "conditions"

# MARKETPLACE
LISTING: str = "listing"
ITEM_LISTING_ID: str = "item_listing_id"
SALE_PRICE: str = "sale_price"
EARNINGS: str = "earnings"
RECALL_REASON_TITLE: str = "recall_reason_title"
RECALL_REASON_DESCRIPTION: str = "recall_reason_description"
STORAGE_FEE: str = "storage_fee"
RECALL_REASON: str = "recall_reason"
NEXT_CHARGE_TIME: str = "next_charge_time"
NEXT_CHARGE_DATE: str = "next_charge_date"
FEE_COUNT: str = "fee_count"
REASON: str = "reason"
STORE_COMMISSION: str = "store_commission"
MIN_LISTING_DAYS: str = "min_listing_days"
ITEM_PRICE: str = "item_price"
TRANSACTION_FEE: str = "transaction_fee"
LISTING_PRICE: str = "listing_price"
STORE_COMMISSION_AMOUNT: str = "store_commission_amount"
MEMBER_EARNINGS: str = "member_earnings"
ITEM_DETAILS: str = "item_details"
SELLER: str = "seller"

# MEMBERS
MEMBER: str = "member"
MEMBERS: str = "members"
PROFILE: str = "profile"
PROFILE_PHOTO: str = "profile_photo"
MEMBER_ID: str = "member_id"
MEMBER_BIO: str = "member_bio"
INSTAGRAM_URL: str = "instagram_url"
LONGITUDE: str = "longitude"
LATITUDE: str = "latitude"
MEMBER_PROFILE: str = "member_profile"
MOBILE: str = "mobile"
SECONDARY_EMAIL: str = "secondary_email"
EMAIL_NOTIFICATIONS: str = "email_notifications"
MOBILE_NOTIFICATIONS: str = "mobile_notifications"

# NOTIFICATIONS
ACTION_TRIGGERED: str = "action_triggered"
NOTIFICATIONS: str = "notifications"
REMINDERS: str = "reminders"
CURRENT_YEAR: str = "current_year"
ACTIVATION_URL: str = "activation_url"
RESET_URL: str = "reset_url"
LOGIN_URL: str = "login_url"
HOW_IT_WORKS_URL: str = "how_it_works_url"
LOGO_URL: str = "logo_url"
COLLECTION_PIN: str = "collection_pin"
ITEM_PAGE_URL: str = "item_page_url"

# STORES
STORE: str = "store"
STORES: str = "stores"
STORE_ID: str = "store_id"
ADDRESS: str = "address"
OPENING_HOURS: str = "opening_hours"
STORE_NAME: str = "store_name"
STORE_BIO: str = "store_bio"
TAG: str = "tag"
TAG_ID: str = "tag_id"
NEW_TAG_ID: str = "new_tag_id"
TAGS: str = "tags"
GROUPS: str = "groups"
PROFILE_PHOTO_URL: str = "profile_photo_url"
QR_CODE: str = "qr_code"
STREET_ADDRESS: str = "street_address"
CITY: str = "city"
STATE: str = "state"
POSTAL_CODE: str = "postal_code"
COUNTRY: str = "country"
GOOGLE_PROFILE_URL: str = "google_profile_url"
WEBSITE_URL: str = "website_url"
DAY_OF_WEEK: str = "day_of_week"
OPENING_TIME: str = "opening_time"
CLOSING_TIME: str = "closing_time"
TIMEZONE: str = "timezone"
IS_CLOSED: str = "is_closed"
NEW_LISTING_NOTIFICATIONS: str = "new_listing_notifications"
SALES_NOTIFICATIONS: str = "sales_notifications"
STOCK_LIMIT: str = "stock_limit"
PHONE: str = "phone"
COMMISSION: str = "commission"
ACTIVE_LISTINGS_COUNT: str = "active_listings_count"
REMAINING_STOCK: str = "remaining_stock"
MIN_PRICE: str = "min_price"
TAG_COUNT: str = "tag_count"

# PAYMENTS
PAYMENT: str = "payment"
PAYMENT_PROVIDERS: str = "payment_providers"
PAYOUT_PROVIDERS: str = "payout_providers"
API_URL: str = "api_url"
DESCRIPTION: str = "description"
PURCHASE: str = "purchase"
AMOUNT: str = "amount"
STORE_AMOUNT: str = "store_amount"
METADATA: str = "metadata"
LINE_ITEMS: str = "line_items"
AMOUNT_TOTAL: str = "amount_total"
BUYER_EMAIL: str = "buyer_email"
CUSTOMER_EMAIL: str = "customer_email"
RECEIPT_EMAIL: str = "receipt_email"
PAYMENT_STATUS: str = "payment_status"
LAST_PAYMENT_ERROR: str = "last_payment_error"
LATEST_CHARGE: str = "latest_charge"
CONNECT: str = "connect"
PALTFORM: str = "platform"
BUSINESS_TYPE: str = "business_type"
CLIENT_SECRET: str = "client_secret"
SESSION_ID: str = "session_id"
ACCOUNT_SESSION: str = "account_session"
ACCEPTING_LISTINGS: str = "accepting_listings"

# TAGANDTAKE
SUPPLY: str = "supply"
SUPPLIES: str = "supplies"
QUANTITY: str = "quantity"
STRIPE_PRICE_ID: str = "stripe_price_id"