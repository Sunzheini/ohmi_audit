from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .models import Audit, Auditor, Customer


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


@admin.register(Audit)
class AuditAdmin(admin.ModelAdmin):
    # Display fields in list view
    list_display = ('name', 'category', 'date', 'is_active', 'created_at', 'updated_at')

    # Fields to search by
    search_fields = ('name', 'description', 'category')

    # Filters in the right sidebar
    list_filter = ('is_active', 'category', 'date', 'created_at')

    # Default ordering
    ordering = ('id',)

    # Fields that are read-only
    readonly_fields = ('created_at', 'updated_at')

    # Fieldsets for edit page
    fieldsets = (
        (None, {'fields': ('name', 'description', 'date', 'is_active', 'category')}),
        ('Media', {'fields': ('image', 'file')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(Auditor)
class AuditorAdmin(admin.ModelAdmin):
    # Display fields in list view
    list_display = ('first_name', 'last_name', 'email', 'phone', 'created_at', 'updated_at')

    # Fields to search by
    search_fields = ('first_name', 'last_name', 'email', 'phone')

    # Filters in the right sidebar
    list_filter = ('created_at', 'updated_at')

    # Default ordering
    ordering = ('id',)

    # Fields that are read-only
    readonly_fields = ('created_at', 'updated_at')

    # Fieldsets for edit page
    fieldsets = (
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'phone')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    # Display fields in list view
    list_display = ('BG_Vor_Nr', 'company_name_en', 'company_name_bg', 'year', 'VAT_number', 'created_at', 'updated_at')

    # Fields to search by
    search_fields = ('BG_Vor_Nr', 'company_name_bg', 'company_name_en', 'VAT_number', 'company_id')

    # Filters in the right sidebar
    list_filter = ('year', 'created_at', 'updated_at')

    # Default ordering
    ordering = ('id',)

    # Fields that are read-only
    readonly_fields = ('created_at', 'updated_at')

    # Fieldsets for edit page
    fieldsets = (
        ('Company Info', {'fields': ('year', 'BG_Vor_Nr', 'company_name_bg', 'company_name_en')}),
        ('Financial Info', {'fields': ('company_id', 'VAT_number')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
