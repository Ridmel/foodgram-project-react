from django.contrib import admin
from django.urls import include, path
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework.routers import DefaultRouter

from recipes.urls import router as recipes_router
from users.urls import router as user_router

router = DefaultRouter()
router.registry.extend(user_router.registry)
router.registry.extend(recipes_router.registry)


api_urls = [
    path("auth/", include("djoser.urls.authtoken")),
    path(
        "users/set_password/",
        DjoserUserViewSet.as_view({"post": "set_password"}),
        name="set_password"
    ),
    path("", include(router.urls)),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(api_urls)),
]
