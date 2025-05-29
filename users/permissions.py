from rest_framework import permissions


class IsPatient(permissions.BasePermission):
    """
    Permission to only allow patients to access the view.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'patient'


class IsDoctor(permissions.BasePermission):
    """
    Permission to only allow doctors to access the view.
    """
    def has_permission(self, request, view):
        doctor_profile = request.user.doctor
        result = request.user.is_authenticated and request.user.role == 'doctor'
        return result


class IsSelf(permissions.BasePermission):
    """Users can only access their own data"""
    def has_object_permission(self, request, view, obj):
        # For User objects
        if hasattr(obj, 'user_id'):
            return obj.user_id == request.user.user_id
            
        # For Patient/Doctor objects
        if hasattr(obj, 'user'):
            return obj.user.user_id == request.user.user_id
        
        return False

class IsAppointmentParticipant(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Patient or Doctor of this appointment
        return (
            obj.patient.user.user_id == request.user.user_id 
            or 
            obj.doctor.user.user_id == request.user.user_id
        )