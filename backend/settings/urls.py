from django.contrib import admin
from django.urls import include, path

api_urls = [
    path("auth/", include("djoser.urls.authtoken")),
    path("", include("users.urls")),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(api_urls)),
]
