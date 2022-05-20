from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Subscription, User


class CustomUserAdmin(UserAdmin):
    search_fields = ("email", "username")
    list_filter = ("email", "username")


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("subscribed", "subscriber")


admin.site.register(User, CustomUserAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
