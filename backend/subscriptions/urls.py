from rest_framework.routers import DefaultRouter

from .views import (
    # SubscriptionCreateDeleteViewSet,
    SubscriptionListViewSet,
)

router = DefaultRouter()
router.register(
    "subscriptions",
    SubscriptionListViewSet,
    basename="subscription_list",
)
# router.register(
#     r"(?P<sub_id>\d+)/subscribe",
#     SubscriptionCreateDeleteViewSet,
#     basename='subscription_create_delete',
# )
