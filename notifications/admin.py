from django.contrib import admin
from .models import Notification, NotificationTemplate


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'notification_type', 'subject', 'status', 'delivery_method', 'scheduled_time')
    list_filter = ('notification_type', 'status', 'delivery_method', 'scheduled_time')
    search_fields = ('recipient__email', 'subject', 'message')
    date_hierarchy = 'scheduled_time'


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ('notification_type', 'subject_template')
    list_filter = ('notification_type',)
    search_fields = ('subject_template', 'message_template')
