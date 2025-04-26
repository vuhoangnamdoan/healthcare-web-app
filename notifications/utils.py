from django.utils import timezone
from datetime import timedelta
from .models import AppointmentReminder, Notification, NotificationTemplate


def schedule_reminders_for_upcoming_appointments(days_ahead=1):
    """
    Schedule reminders for appointments that are scheduled for X days in the future.
    
    Args:
        days_ahead (int): Number of days ahead to schedule reminders for
        
    Returns:
        int: Number of reminders created
    """
    # Import here to avoid circular imports
    from appointments.models import Appointment
    
    # Calculate the target date (X days from now)
    target_date = timezone.now().date() + timedelta(days=days_ahead)
    
    # Find all scheduled or confirmed appointments for the target date
    appointments = Appointment.objects.filter(
        date=target_date,
        status__in=['scheduled', 'confirmed']
    )
    
    reminders_created = 0
    
    # Try to get a template, or use default message
    try:
        template = NotificationTemplate.objects.get(
            template_type='appointment_reminder',
            is_active=True
        )
    except NotificationTemplate.DoesNotExist:
        template = None
    
    for appointment in appointments:
        # Create reminder time for 8 AM on appointment day
        reminder_time = timezone.datetime.combine(
            appointment.date, 
            timezone.datetime.strptime("08:00", "%H:%M").time()
        )
        reminder_time = timezone.make_aware(reminder_time)
        
        # Check if reminders already exist for this appointment
        existing_reminders = AppointmentReminder.objects.filter(
            appointment_id=appointment.appointment_id,
            status='pending'
        )
        
        if existing_reminders.exists():
            continue
            
        # Create message for patient
        if template:
            patient_message = template.content.format(
                patient_name=f"{appointment.patient.first_name} {appointment.patient.last_name}",
                doctor_name=f"{appointment.doctor.first_name} {appointment.doctor.last_name}",
                date=appointment.date.strftime("%B %d, %Y"),
                time=appointment.start_time.strftime("%I:%M %p"),
                location="Online",
                duration=f"{appointment.duration_minutes} minutes"
            )
        else:
            patient_message = (
                f"Reminder: You have an appointment with Dr. {appointment.doctor.last_name} "
                f"on {appointment.date.strftime('%B %d, %Y')} at {appointment.start_time.strftime('%I:%M %p')}. "
                f"Please be on time."
            )
        
        # Create reminder for patient
        AppointmentReminder.objects.create(
            appointment_id=appointment.appointment_id,
            recipient=appointment.patient,
            scheduled_time=reminder_time,
            message=patient_message,
            status='pending'
        )
        reminders_created += 1
        
        # Create message for doctor
        doctor_message = (
            f"Reminder: You have an appointment with {appointment.patient.first_name} "
            f"{appointment.patient.last_name} scheduled for {appointment.date.strftime('%B %d, %Y')} "
            f"at {appointment.start_time.strftime('%I:%M %p')}."
        )
        
        # Create reminder for doctor
        AppointmentReminder.objects.create(
            appointment_id=appointment.appointment_id,
            recipient=appointment.doctor,
            scheduled_time=reminder_time,
            message=doctor_message,
            status='pending'
        )
        reminders_created += 1
    
    return reminders_created


def process_pending_reminders():
    """
    Process all pending reminders that are due to be sent.
    
    Returns:
        int: Number of reminders processed
    """
    now = timezone.now()
    
    # Get all pending reminders scheduled for now or earlier
    pending_reminders = AppointmentReminder.objects.filter(
        status='pending',
        scheduled_time__lte=now
    )
    
    processed_count = 0
    
    for reminder in pending_reminders:
        # Create a notification from the reminder
        Notification.objects.create(
            recipient=reminder.recipient,
            title="Appointment Reminder",
            message=reminder.message,
            notification_type='appointment_reminder',
            appointment_id=reminder.appointment_id,
            status='unread'
        )
        
        # Mark the reminder as sent
        reminder.mark_as_sent()
        processed_count += 1
    
    return processed_count


def cancel_reminder(appointment_id):
    """
    Cancel all pending reminders for a specific appointment
    
    Args:
        appointment_id (str): The appointment ID to cancel reminders for
        
    Returns:
        int: Number of reminders cancelled
    """
    reminders = AppointmentReminder.objects.filter(
        appointment_id=appointment_id,
        status='pending'
    )
    
    count = reminders.count()
    reminders.update(status='cancelled')
    
    return count


def reschedule_reminder(appointment_id, new_date):
    """
    Reschedule reminders for an appointment that has been rescheduled
    
    Args:
        appointment_id (str): The appointment ID
        new_date (date): The new date for the appointment
        
    Returns:
        int: Number of reminders rescheduled
    """
    # Cancel existing reminders
    cancel_reminder(appointment_id)
    
    # Import here to avoid circular imports
    from appointments.models import Appointment
    
    try:
        # Get the appointment
        appointment = Appointment.objects.get(appointment_id=appointment_id)
        
        # Create new reminders for the new date
        reminder_time = timezone.datetime.combine(
            new_date, 
            timezone.datetime.strptime("08:00", "%H:%M").time()
        )
        reminder_time = timezone.make_aware(reminder_time)
        
        # Create patient reminder
        patient_message = (
            f"Updated Reminder: Your appointment with Dr. {appointment.doctor.last_name} "
            f"has been rescheduled to {new_date.strftime('%B %d, %Y')} at "
            f"{appointment.start_time.strftime('%I:%M %p')}."
        )
        
        AppointmentReminder.objects.create(
            appointment_id=appointment_id,
            recipient=appointment.patient,
            scheduled_time=reminder_time,
            message=patient_message,
            status='pending'
        )
        
        # Create doctor reminder
        doctor_message = (
            f"Updated Reminder: Your appointment with {appointment.patient.first_name} "
            f"{appointment.patient.last_name} has been rescheduled to {new_date.strftime('%B %d, %Y')} "
            f"at {appointment.start_time.strftime('%I:%M %p')}."
        )
        
        AppointmentReminder.objects.create(
            appointment_id=appointment_id,
            recipient=appointment.doctor,
            scheduled_time=reminder_time,
            message=doctor_message,
            status='pending'
        )
        
        return 2
    except Appointment.DoesNotExist:
        return 0


def create_appointment_notification(appointment, action_type):
    """
    Create notifications for both doctor and patient about appointment status changes.
    
    Args:
        appointment: The Appointment object
        action_type (str): Type of action - 'created', 'cancelled', 'confirmed', 'completed', 'rescheduled'
        
    Returns:
        list: Created notification objects
    """
    notifications = []
    
    # Set notification type based on action
    notification_type = f'appointment_{action_type}'
    
    # Set titles and messages based on action type
    if action_type == 'created':
        patient_title = "New Appointment Scheduled"
        patient_message = (
            f"You have scheduled a new appointment with Dr. {appointment.doctor.last_name} on "
            f"{appointment.date.strftime('%B %d, %Y')} at {appointment.start_time.strftime('%I:%M %p')}."
        )
        
        doctor_title = "New Appointment Request"
        doctor_message = (
            f"A new appointment has been scheduled with {appointment.patient.first_name} "
            f"{appointment.patient.last_name} on {appointment.date.strftime('%B %d, %Y')} "
            f"at {appointment.start_time.strftime('%I:%M %p')}."
        )
    
    elif action_type == 'cancelled':
        patient_title = "Appointment Cancelled"
        patient_message = (
            f"Your appointment with Dr. {appointment.doctor.last_name} on "
            f"{appointment.date.strftime('%B %d, %Y')} at {appointment.start_time.strftime('%I:%M %p')} "
            f"has been cancelled."
        )
        
        doctor_title = "Appointment Cancelled"
        doctor_message = (
            f"The appointment with {appointment.patient.first_name} {appointment.patient.last_name} on "
            f"{appointment.date.strftime('%B %d, %Y')} at {appointment.start_time.strftime('%I:%M %p')} "
            f"has been cancelled."
        )
        
        if appointment.cancellation_reason:
            patient_message += f" Reason: {appointment.cancellation_reason}"
            doctor_message += f" Reason: {appointment.cancellation_reason}"
    
    elif action_type == 'confirmed':
        patient_title = "Appointment Confirmed"
        patient_message = (
            f"Your appointment with Dr. {appointment.doctor.last_name} on "
            f"{appointment.date.strftime('%B %d, %Y')} at {appointment.start_time.strftime('%I:%M %p')} "
            f"has been confirmed."
        )
        
        doctor_title = "Appointment Confirmed"
        doctor_message = (
            f"You have confirmed the appointment with {appointment.patient.first_name} "
            f"{appointment.patient.last_name} on {appointment.date.strftime('%B %d, %Y')} "
            f"at {appointment.start_time.strftime('%I:%M %p')}."
        )
    
    elif action_type == 'completed':
        patient_title = "Appointment Completed"
        patient_message = (
            f"Your appointment with Dr. {appointment.doctor.last_name} on "
            f"{appointment.date.strftime('%B %d, %Y')} has been marked as completed."
        )
        
        doctor_title = "Appointment Completed"
        doctor_message = (
            f"The appointment with {appointment.patient.first_name} {appointment.patient.last_name} on "
            f"{appointment.date.strftime('%B %d, %Y')} has been marked as completed."
        )
    
    elif action_type == 'rescheduled':
        patient_title = "Appointment Rescheduled"
        patient_message = (
            f"Your appointment with Dr. {appointment.doctor.last_name} has been rescheduled to "
            f"{appointment.date.strftime('%B %d, %Y')} at {appointment.start_time.strftime('%I:%M %p')}."
        )
        
        doctor_title = "Appointment Rescheduled"
        doctor_message = (
            f"The appointment with {appointment.patient.first_name} {appointment.patient.last_name} "
            f"has been rescheduled to {appointment.date.strftime('%B %d, %Y')} "
            f"at {appointment.start_time.strftime('%I:%M %p')}."
        )
    
    else:
        # Default messaging for unknown action types
        patient_title = "Appointment Update"
        patient_message = f"Your appointment status has been updated to: {action_type}"
        doctor_title = "Appointment Update"
        doctor_message = f"An appointment status has been updated to: {action_type}"
    
    # Create notification for patient
    patient_notification = Notification.objects.create(
        recipient=appointment.patient,
        title=patient_title,
        message=patient_message,
        notification_type=notification_type,
        appointment_id=appointment.appointment_id,
        status='unread'
    )
    notifications.append(patient_notification)
    
    # Create notification for doctor
    doctor_notification = Notification.objects.create(
        recipient=appointment.doctor,
        title=doctor_title,
        message=doctor_message,
        notification_type=notification_type,
        appointment_id=appointment.appointment_id,
        status='unread'
    )
    notifications.append(doctor_notification)
    
    return notifications


def schedule_appointment_reminders(appointment):
    """
    Schedule reminders for a newly created appointment
    
    Args:
        appointment: The Appointment object
        
    Returns:
        int: Number of reminders created (0-2)
    """
    # Only schedule reminders for future appointments
    today = timezone.now().date()
    
    # If appointment is today or in the past, don't schedule reminders
    if appointment.date <= today:
        return 0
    
    reminder_count = 0
    
    # Create reminder time for 8 AM on appointment day
    reminder_time = timezone.datetime.combine(
        appointment.date, 
        timezone.datetime.strptime("08:00", "%H:%M").time()
    )
    reminder_time = timezone.make_aware(reminder_time)
    
    # Try to get a template, or use default message
    try:
        template = NotificationTemplate.objects.get(
            template_type='appointment_reminder',
            is_active=True
        )
    except NotificationTemplate.DoesNotExist:
        template = None
    
    # Create message for patient
    if template:
        patient_message = template.content.format(
            patient_name=f"{appointment.patient.first_name} {appointment.patient.last_name}",
            doctor_name=f"{appointment.doctor.first_name} {appointment.doctor.last_name}",
            date=appointment.date.strftime("%B %d, %Y"),
            time=appointment.start_time.strftime("%I:%M %p"),
            location="Online",
            duration=f"{appointment.duration_minutes} minutes"
        )
    else:
        patient_message = (
            f"Reminder: You have an appointment with Dr. {appointment.doctor.last_name} "
            f"on {appointment.date.strftime('%B %d, %Y')} at {appointment.start_time.strftime('%I:%M %p')}. "
            f"Please be on time."
        )
    
    # Create reminder for patient
    AppointmentReminder.objects.create(
        appointment_id=appointment.appointment_id,
        recipient=appointment.patient,
        scheduled_time=reminder_time,
        message=patient_message,
        status='pending'
    )
    reminder_count += 1
    
    # Create message for doctor
    doctor_message = (
        f"Reminder: You have an appointment with {appointment.patient.first_name} "
        f"{appointment.patient.last_name} scheduled for {appointment.date.strftime('%B %d, %Y')} "
        f"at {appointment.start_time.strftime('%I:%M %p')}."
    )
    
    # Create reminder for doctor
    AppointmentReminder.objects.create(
        appointment_id=appointment.appointment_id,
        recipient=appointment.doctor,
        scheduled_time=reminder_time,
        message=doctor_message,
        status='pending'
    )
    reminder_count += 1
    
    return reminder_count