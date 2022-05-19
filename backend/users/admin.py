from django.contrib import admin

from .models import Subscription, User


class CustomUserAdmin(admin.ModelAdmin):
    pass


class SubscriptionAdmin(admin.ModelAdmin):
    pass


admin.site.register(User, CustomUserAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
