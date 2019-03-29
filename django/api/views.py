from django.shortcuts import render
from django.views.generic import TemplateView

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from . import models
from rest_framework import viewsets
from rest_social_auth.views import SocialJWTUserAuthView
from . import serializers as ApiSerializers

from rest_framework import serializers

# Create your views here.
class ApiHomeView(TemplateView):
    template_name = 'api/api-index.html'

    def get(self, request, *arg, **kwargs):
        print("Hey ya! Index view accessed, user is:", request.user)
        return super().get(request, *arg, **kwargs)


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = get_user_model().objects.all().order_by('-date_joined')
    serializer_class = ApiSerializers.UserSerializer

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            # anonymous user
            raise PermissionError
        elif not self.request.user.is_superuser:
            # regular user
            return get_user_model().objects.filter(uuid=self.request.user.uuid)
        else:
            # admin user
            return get_user_model().objects.all().order_by('-date_joined')


class SocialAuthView(SocialJWTUserAuthView):
      serializer_class = ApiSerializers.SocialAuthUserSerializer


"""
    REST API
"""

class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = ApiSerializers.GroupSerializer

class AddressViewSet(viewsets.ModelViewSet):
    queryset = models.Address.objects.all()
    serializer_class = ApiSerializers.AddressSerializer

class LinkViewSet(viewsets.ModelViewSet):
    queryset = models.Link.objects.all()
    serializer_class = ApiSerializers.LinkSerializer

class CompanyViewSet(viewsets.ModelViewSet):
    queryset = models.Company.objects.all()
    serializer_class = ApiSerializers.CompanySerializer

    def create(self, request):
        """
            Entry point for POST request.
            CompanyViewSet.create() => 
            .is_valid() based on serializer's fields => 
            CompanyViewSet.perform_create() =>
            CompanySerializer.create()
        """
        serializer = ApiSerializers.CompanySerializer(data=request.data)
        return super(CompanyViewSet, self).create(request)
    
    def perform_create(self, serializer):
        """
            After .is_valid() call:
            The create() method of our serializer will now be passed 
            an additional 'user' field, along with the validated data from the request.
        """
        serializer.save(user=self.request.user)
    

class CompanyRatingViewSet(viewsets.ModelViewSet):
    queryset = models.CompanyRating.objects.all()
    serializer_class = ApiSerializers.CompanyRatingSerializer

class LabelViewSet(viewsets.ModelViewSet):
    queryset = models.Label.objects.all()
    serializer_class = ApiSerializers.LabelSerializer

class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = models.Application.objects.all()
    serializer_class = ApiSerializers.ApplicationSerializer

class PositionLocationViewSet(viewsets.ModelViewSet):
    queryset = models.PositionLocation.objects.all()
    serializer_class = ApiSerializers.PositionLocationSerializer

class ApplicationStatusViewSet(viewsets.ModelViewSet):
    queryset = models.ApplicationStatus.objects.all()
    serializer_class = ApiSerializers.ApplicationStatusSerializer

class ApplicationStatusLinkViewSet(viewsets.ModelViewSet):
    queryset = models.ApplicationStatusLink.objects.all()
    serializer_class = ApiSerializers.ApplicationStatusLinkSerializer

