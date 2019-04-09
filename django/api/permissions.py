from rest_framework import permissions

class OwnerOnlyObjectPermission(permissions.BasePermission):
    """
    Handles permissions for users.  The basic rules are

     - owner may GET, PUT, POST, DELETE
     - nobody else can access
     """

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return super(self.__class__, self).has_object_permission(request, view, obj)
        
        # check if user is owner
        print("="*10)
        try:
            print("obj permimsion check! request.user vs obj.user=", request.user, obj.user)
            return request.user == obj.user
        except AttributeError:
            # no user attribute on model object
            return super().has_object_permission(request, view, obj)