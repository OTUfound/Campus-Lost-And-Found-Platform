from django.contrib import admin
from .models import CustomUser, LostFoundItem, PasswordResetToken, EmailVerificationToken, Claim


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['email', 'first_name', 'last_name', 'is_verified', 'is_staff']
    list_filter = ['is_verified', 'is_staff', 'date_joined']
    search_fields = ['email', 'first_name', 'last_name']


@admin.register(LostFoundItem)
class LostFoundItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'item_type', 'category', 'status', 'posted_by', 'created_at']
    list_filter = ['item_type', 'category', 'status', 'created_at']
    search_fields = ['title', 'description', 'location']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'expires_at', 'is_used']
    list_filter = ['created_at', 'expires_at', 'is_used']
    search_fields = ['user__email']
    readonly_fields = ['created_at']


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'expires_at', 'is_used']
    list_filter = ['created_at', 'expires_at', 'is_used']
    search_fields = ['user__email']
    readonly_fields = ['created_at']


@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    list_display = ['item', 'claimant', 'status', 'created_at', 'approved_at']
    list_filter = ['status', 'created_at', 'approved_at']
    search_fields = ['item__title', 'claimant__email']
    readonly_fields = ['created_at', 'updated_at']

