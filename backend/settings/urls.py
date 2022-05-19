from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework.routers import DefaultRouter

from django.conf import settings
from django.contrib import admin
from django.urls import include, path

from recipes.urls import router as recipe_router
from users.urls import router as user_router

router = DefaultRouter()
router.registry.extend(user_router.registry)
router.registry.extend(recipe_router.registry)

api_urls = [
    path("auth/", include("djoser.urls.authtoken")),
    path(
        "users/set_password/",
        DjoserUserViewSet.as_view({"post": "set_password"}),
        name="set_password",
    ),
    path("", include(router.urls)),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(api_urls)),
]

if settings.DEBUG:
    urlpatterns += [path("debug/", include("debug_toolbar.urls"))]
