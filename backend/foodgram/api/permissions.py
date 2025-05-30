from rest_framework import permissions


class AuthorOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user == obj.author
        )


class CurrentUserOrAdminOrAnonymousReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return not (request.user.is_anonymous and view.action == 'me')

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or (request.user.is_authenticated
                and (request.user == obj or request.user.is_staff))
        )
