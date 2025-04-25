from django.core.management.base import BaseCommand
from django.utils import timezone
from notifications.utils import process_pending_reminders


class Command(BaseCommand):
    help = 'Process all due appointment reminders and send notifications'

    def handle(self, *args, **options):
        start_time = timezone.now()
        self.stdout.write(self.style.SUCCESS(
            f'Processing due appointment reminders at {start_time}'))
        
        reminders_processed = process_pending_reminders()
        
        end_time = timezone.now()
        duration = (end_time - start_time).total_seconds()
        
        self.stdout.write(self.style.SUCCESS(
            f'Processed {reminders_processed} reminders in {duration:.2f} seconds'))