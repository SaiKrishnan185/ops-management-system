from django.core.exceptions import PermissionDenied

def admin_required(user):
    if user.userprofile.role != 'ADMIN':
        raise PermissionDenied


def staff_required(user):
    if user.userprofile.role != 'STAFF':
        raise PermissionDenied
