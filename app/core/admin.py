from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext as _

from core import models


class UserAdmin(BaseUserAdmin):
    """Admin view configuration for User model."""

    # list page
    ordering = ['id']
    list_display = ['email', 'name']

    # Edit Page
    fieldsets = (
        (_('Login Credentials'), {'fields': ('email', 'password')}),
        (_('Personal Information'), {'fields': ('name',)}),
        (_('Permissions'),
         {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        (_('Important Dates'), {'fields': ('last_login',)})
    )

    # Insertion Page
    add_fieldsets = (
        (_('Login Credentials'), {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Tag)
admin.site.register(models.Ingredient)
