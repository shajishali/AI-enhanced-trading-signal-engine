from django.contrib import admin
from django.utils.html import format_html
from .models import SubscriptionPlan, UserProfile, Payment, SubscriptionHistory

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'tier', 'price', 'currency', 'billing_cycle', 'is_active', 'max_signals_per_day']
    list_filter = ['tier', 'billing_cycle', 'is_active', 'has_ml_predictions', 'has_api_access']
    search_fields = ['name', 'tier']
    ordering = ['price']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'tier', 'price', 'currency', 'billing_cycle', 'is_active')
        }),
        ('Feature Limits', {
            'fields': ('max_signals_per_day', 'max_portfolios', 'has_ml_predictions', 'has_api_access', 'has_priority_support')
        }),
        ('Trial Settings', {
            'fields': ('trial_days',)
        }),
    )

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'subscription_plan', 'subscription_status', 'is_subscription_active', 'signals_used_today', 'email_verified']
    list_filter = ['subscription_status', 'subscription_plan', 'email_verified', 'social_provider']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at', 'updated_at', 'last_signal_reset']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'email_verified', 'profile_picture')
        }),
        ('Subscription Information', {
            'fields': ('subscription_plan', 'subscription_status', 'subscription_start_date', 'subscription_end_date', 'trial_end_date')
        }),
        ('Social Authentication', {
            'fields': ('social_provider', 'social_id'),
            'classes': ('collapse',)
        }),
        ('Usage Tracking', {
            'fields': ('signals_used_today', 'last_signal_reset'),
            'classes': ('collapse',)
        }),
        ('Preferences', {
            'fields': ('notification_preferences',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def is_subscription_active(self, obj):
        if obj.is_subscription_active:
            return format_html('<span style="color: green;">✓ Active</span>')
        else:
            return format_html('<span style="color: red;">✗ Inactive</span>')
    is_subscription_active.short_description = 'Subscription Active'

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['user', 'subscription_plan', 'amount', 'currency', 'status', 'provider', 'created_at']
    list_filter = ['status', 'provider', 'currency', 'created_at']
    search_fields = ['user__email', 'provider_payment_id']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('user', 'subscription_plan', 'amount', 'currency', 'status')
        }),
        ('Provider Information', {
            'fields': ('provider', 'provider_payment_id')
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(SubscriptionHistory)
class SubscriptionHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'old_plan', 'new_plan', 'created_at']
    list_filter = ['action', 'created_at']
    search_fields = ['user__email']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Subscription Change', {
            'fields': ('user', 'action', 'old_plan', 'new_plan', 'payment')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
