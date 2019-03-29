from django.shortcuts import render
from django.views.generic import TemplateView

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from . import models
from rest_framework import viewsets
from rest_social_auth.views import SocialJWTUserAuthView
from . import serializers

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
    serializer_class = serializers.UserSerializer

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
      serializer_class = serializers.SocialAuthUserSerializer


"""
    REST API
"""

class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = serializers.GroupSerializer

class CompanyViewSet(viewsets.ModelViewSet):
    queryset = models.Company.objects.all()
    serializer_class = serializers.CompanySerializer

class CompanyRatingViewSet(viewsets.ModelViewSet):
    queryset = models.CompanyRating.objects.all()
    serializer_class = serializers.CompanyRatingSerializer

class AddressViewSet(viewsets.ModelViewSet):
    queryset = models.Address.objects.all()
    serializer_class = serializers.AddressSerializer

class LinkViewSet(viewsets.ModelViewSet):
    queryset = models.Link.objects.all()
    serializer_class = serializers.LinkSerializer

class LabelViewSet(viewsets.ModelViewSet):
    queryset = models.Label.objects.all()
    serializer_class = serializers.LabelSerializer

class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = models.Application.objects.all()
    serializer_class = serializers.ApplicationSerializer

class PositionLocationViewSet(viewsets.ModelViewSet):
    queryset = models.PositionLocation.objects.all()
    serializer_class = serializers.PositionLocationSerializer

class ApplicationStatusViewSet(viewsets.ModelViewSet):
    queryset = models.ApplicationStatus.objects.all()
    serializer_class = serializers.ApplicationStatusSerializer

class ApplicationStatusLinkViewSet(viewsets.ModelViewSet):
    queryset = models.ApplicationStatusLink.objects.all()
    serializer_class = serializers.ApplicationStatusLinkSerializer

