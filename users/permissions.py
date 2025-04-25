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
        return request.user.is_authenticated and request.user.role == 'doctor'


class IsAdmin(permissions.BasePermission):
    """
    Permission to only allow administrators to access the view.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.user.role == 'admin' or request.user.is_superuser)


class IsSelfOrAdmin(permissions.BasePermission):
    """
    Object-level permission to only allow users to edit their own profile or admins to edit anyone.
    """
    def has_object_permission(self, request, view, obj):
        # Admin permissions
        if request.user.role == 'admin' or request.user.is_superuser:
            return True
            
        # Users can only access their own profiles
        return obj.id == request.user.id


class IsDoctorOrAdmin(permissions.BasePermission):
    """
    Permission to only allow doctors to access their own medical content or admins to access any.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.role == 'doctor' or
            request.user.role == 'admin' or
            request.user.is_superuser
        )
        
    def has_object_permission(self, request, view, obj):
        # Admin can access anything
        if request.user.role == 'admin' or request.user.is_superuser:
            return True
            
        # For objects with a doctor attribute
        if hasattr(obj, 'doctor'):
            return obj.doctor.id == request.user.id
            
        return False


class IsAppointmentParticipant(permissions.BasePermission):
    """
    Permission to only allow participants in an appointment to access it.
    """
    def has_object_permission(self, request, view, obj):
        # Admin permissions
        if request.user.role == 'admin' or request.user.is_superuser:
            return True
            
        # Check if user is the patient or doctor of this appointment
        return (obj.patient.id == request.user.id or 
                obj.doctor.id == request.user.id)