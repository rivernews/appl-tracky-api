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
        if obj.user:
            print("obj permimsion check! request.user/obj=", request.user, obj)
            return request.user == obj.user
        else:
            return super(self.__class__, self).has_object_permission(request, view, obj)