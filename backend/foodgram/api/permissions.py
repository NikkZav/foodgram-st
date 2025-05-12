from rest_framework import permissions


class UserPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action in ("list", "retrieve", "get_link"):
            return True  # GET+POST /api/users/ и GET /api/users/{id}/ — доступны всем
        return request.user.is_authenticated  # остальные — только для авторизованных

    def has_object_permission(self, request, view, obj):
        if view.action in ("update", "partial_update", "destroy",):
            return request.user.is_authenticated and \
                request.user == obj.author  # PATCH и DELETE — только для автора
        return True  # GET /api/users/{id}/ — доступен всем, кто прошел has_permission
