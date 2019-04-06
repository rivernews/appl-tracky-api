from django.shortcuts import render
from django.views.generic import TemplateView
from django.core.exceptions import FieldDoesNotExist

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from . import models
from rest_framework import viewsets
from rest_social_auth.views import SocialJWTUserAuthView
from . import serializers as ApiSerializers

from rest_framework import serializers

from . import permissions as ApiPermissions

# Create your views here.
class ApiHomeView(TemplateView):
    template_name = 'api/api-index.html'

    def get(self, request, *arg, **kwargs):
        print("Hey ya! Index view accessed, user is:", request.user)
        return super().get(request, *arg, **kwargs)


class SocialAuthView(SocialJWTUserAuthView):
      serializer_class = ApiSerializers.SocialAuthUserSerializer


"""
    REST API
"""

class BaseModelViewSet(viewsets.ModelViewSet):
    
    model = None
    permission_classes = (ApiPermissions.OwnerOnlyObjectPermission,)

    def get_queryset(self):
        print("="*10)

        if self.request.user.is_superuser:
            return self.model.objects.all()
        elif not self.request.user.is_authenticated:
            print("user not login", self.request.user)
            raise PermissionError
        
        # restrict access for owner-only models
        if self.is_user_field_exist():
            return self.model.objects.filter(user=self.request.user)
        else:
            return self.model.objects.all()
    
    def is_user_field_exist(self):
        try:
            self.model._meta.get_field('user')
            return True
        except FieldDoesNotExist:
            return False
    
    def perform_create(self, serializer):
        """
            After serializer's .is_valid() call:
            The create() method of our serializer will now be passed 
            an additional 'user' field, along with the validated data from the request.
            
            refer to: https://www.django-rest-framework.org/tutorial/4-authentication-and-permissions/
        """
        if self.is_user_field_exist():
            serializer.save(user=self.request.user)
        else:
            serializer.save()

class UserViewSet(BaseModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    model = get_user_model()
    queryset = get_user_model().objects.none() # for router to figure out basename for model
    serializer_class = ApiSerializers.UserSerializer

    def get_queryset(self):
        queryset = super(self.__class__, self).get_queryset()
        # only allow the user get his/her own user obj
        return queryset.filter(uuid=self.request.user.uuid)

class GroupViewSet(BaseModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    model = Group
    queryset = Group.objects.none()
    serializer_class = ApiSerializers.GroupSerializer

class AddressViewSet(BaseModelViewSet):
    model = models.Address
    queryset = models.Address.objects.none()
    serializer_class = ApiSerializers.AddressSerializer

class LinkViewSet(BaseModelViewSet):
    model = models.Link
    queryset = models.Link.objects.none()
    serializer_class = ApiSerializers.LinkSerializer

class CompanyViewSet(BaseModelViewSet):
    model = models.Company
    queryset = models.Company.objects.none()
    serializer_class = ApiSerializers.CompanySerializer

    # def create(self, request):
    #     """
    #         Entry point for POST request.
    #         CompanyViewSet.create() => 
    #         .is_valid() based on serializer's fields => 
    #         CompanyViewSet.perform_create() =>
    #         CompanySerializer.create()
    #     """
    #     # you can inspect serializer and .is_valid() here
    #     serializer = self.serializer_class(data=request.data)
    #     print("Is valid?", serializer.is_valid())
    #     import ipdb; ipdb.set_trace()
    #     return super(CompanyViewSet, self).create(request)


class CompanyRatingViewSet(BaseModelViewSet):
    model = models.CompanyRating
    queryset = models.CompanyRating.objects.none()
    serializer_class = ApiSerializers.CompanyRatingSerializer

class LabelViewSet(BaseModelViewSet):
    model = models.Label
    queryset = models.Label.objects.none()
    serializer_class = ApiSerializers.LabelSerializer

class ApplicationViewSet(BaseModelViewSet):
    model = models.Application
    queryset = models.Application.objects.none()
    serializer_class = ApiSerializers.ApplicationSerializer

class PositionLocationViewSet(BaseModelViewSet):
    model = models.PositionLocation
    queryset = models.PositionLocation.objects.none()
    serializer_class = ApiSerializers.PositionLocationSerializer

class ApplicationStatusViewSet(BaseModelViewSet):
    model = models.ApplicationStatus
    queryset = models.ApplicationStatus.objects.none()
    serializer_class = ApiSerializers.ApplicationStatusSerializer

class ApplicationStatusLinkViewSet(BaseModelViewSet):
    model = models.ApplicationStatusLink
    queryset = models.ApplicationStatusLink.objects.none()
    serializer_class = ApiSerializers.ApplicationStatusLinkSerializer

