from django.contrib import admin
from .models import Notification, NotificationTemplate


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'notification_type', 'subject', 'status', 'scheduled_time')
    list_filter = ('notification_type', 'status', 'scheduled_time')
    search_fields = ('recipient__email', 'subject', 'message', 'appointment_id')
    date_hierarchy = 'scheduled_time'
    fieldsets = (
        (None, {
            'fields': ('recipient', 'appointment_id', 'notification_type')
        }),
        ('Content', {
            'fields': ('subject', 'message')
        }),
        ('Status', {
            'fields': ('status', 'failure_reason', 'retry_count', 'max_retries')
        }),
        ('Timing', {
            'fields': ('scheduled_time', 'sent_time')
        }),
    )


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ('notification_type', 'subject_template', 'days_before', 'hours_before')
    list_filter = ('notification_type',)
    search_fields = ('subject_template', 'message_template')
