from django.urls import include, path
from rest_framework.routers import DefaultRouter
from djoser.views import UserViewSet as DjoserUserViewSet

from .views import UserViewSet

router = DefaultRouter()
router.register("users", UserViewSet, basename="user")

urlpatterns = [
    path(
        "users/set_password/",
        DjoserUserViewSet.as_view({"post": "set_password"}),
        name="set_password"
    ),
    path("", include(router.urls)),
]

