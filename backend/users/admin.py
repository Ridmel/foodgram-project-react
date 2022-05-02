from django.contrib import admin

from .models import User


class CustomUserAdmin(admin.ModelAdmin):
    pass


admin.site.register(User, CustomUserAdmin)
