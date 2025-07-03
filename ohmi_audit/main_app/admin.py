from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin


UserModel = get_user_model()


@admin.register(UserModel)
class AppUserAdmin(UserAdmin):
    # Display fields in list view
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')

    # Fields to search by
    search_fields = ('username', 'email', 'first_name', 'last_name')

    # Default ordering
    ordering = ('username',)

    # Fieldsets for edit page
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )

    # Fields for add page
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )
