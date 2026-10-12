from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    message = 'You must be the owner of this object.'

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user