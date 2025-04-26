from django.core.management.base import BaseCommand
from django.utils import timezone
from notifications.utils import schedule_reminders_for_upcoming_appointments


class Command(BaseCommand):
    help = 'Schedule reminders for upcoming appointments'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Schedule reminders for appointments in the next X days'
        )

    def handle(self, *args, **options):
        days = options['days']
        start_time = timezone.now()
        self.stdout.write(self.style.SUCCESS(
            f'Scheduling reminders for appointments in the next {days} days at {start_time}'))
        
        reminders_created = 0
        
        # Process each day in the specified range
        for day in range(1, days + 1):
            daily_reminders = schedule_reminders_for_upcoming_appointments(day)
            reminders_created += daily_reminders
            self.stdout.write(f'  Created {daily_reminders} reminders for appointments {day} days ahead')
        
        end_time = timezone.now()
        duration = (end_time - start_time).total_seconds()
        
        self.stdout.write(self.style.SUCCESS(
            f'Scheduled {reminders_created} reminders in {duration:.2f} seconds'))