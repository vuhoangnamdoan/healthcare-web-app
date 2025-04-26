from django.contrib import admin
from .models import Notification, NotificationTemplate, AppointmentReminder


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'notification_type', 'title', 'status', 'created_at')
    list_filter = ('notification_type', 'status', 'created_at')
    search_fields = ('recipient__email', 'title', 'message', 'appointment_id')
    date_hierarchy = 'created_at'
    fieldsets = (
        (None, {
            'fields': ('recipient', 'appointment_id', 'notification_type')
        }),
        ('Content', {
            'fields': ('title', 'message')
        }),
        ('Status', {
            'fields': ('status', 'read_at')
        }),
        ('Timing', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    readonly_fields = ('created_at', 'updated_at', 'read_at')


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'template_type', 'is_active', 'created_at')
    list_filter = ('template_type', 'is_active')
    search_fields = ('name', 'content')
    fieldsets = (
        (None, {
            'fields': ('name', 'template_type', 'is_active')
        }),
        ('Content', {
            'fields': ('content',)
        }),
        ('Timing', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    readonly_fields = ('created_at', 'updated_at')


@admin.register(AppointmentReminder)
class AppointmentReminderAdmin(admin.ModelAdmin):
    list_display = ('appointment_id', 'recipient', 'status', 'scheduled_time')
    list_filter = ('status', 'scheduled_time')
    search_fields = ('appointment_id', 'recipient__email', 'message')
    date_hierarchy = 'scheduled_time'
    fieldsets = (
        (None, {
            'fields': ('appointment_id', 'recipient')
        }),
        ('Content', {
            'fields': ('message',)
        }),
        ('Status', {
            'fields': ('status', 'sent_at')
        }),
        ('Timing', {
            'fields': ('scheduled_time', 'created_at', 'updated_at')
        }),
    )
    readonly_fields = ('created_at', 'updated_at', 'sent_at')
