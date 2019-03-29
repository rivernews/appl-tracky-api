from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from . import models
from rest_framework import serializers
from rest_social_auth.serializers import UserJWTSerializer


class UserSerializer(serializers.HyperlinkedModelSerializer):
    """
    For general API endpoint
    """
    class Meta:
        model = get_user_model()
        fields = ('url', 'email', 'first_name', 'last_name')


class SocialAuthUserSerializer(UserJWTSerializer):
    """
    For social login endpoint to decide what to respond to frontend upon login (work with JWT)
    """
    class Meta:
        model = get_user_model()
        exclude = UserJWTSerializer.Meta.exclude + ('uuid', 'username',)


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')

"""
    Main Data Model
"""

class CompanySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Company
        fields = ('url', 'uuid', 'user', 'labels', 'name', 'hq_location', 'home_page', 'modified_at')

class CompanyRatingSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.CompanyRating
        fields = ('url', 'uuid', 'source', 'value', 'company', 'sample_date', 'modified_at')

class AddressSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Address
        fields = ('url', 'uuid', 'place_name', 'country', 'state', 'street', 'full_address', 'zipcode', 'modified_at')

class LinkSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Link
        fields = ('url', 'uuid', 'text', 'user', 'url', 'order', 'modified_at')

class LabelSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Label
        fields = ('url', 'uuid', 'user', 'text', 'color', 'order', 'modified_at')

class ApplicationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Application
        fields = (
            'url', 'uuid', 'user', 
            'user_company', 'position_title', 
            'job_description_page', 'job_source', 
            'labels', 'modified_at')

class PositionLocationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.PositionLocation
        fields = ('url', 'uuid', 'application', 'location', 'modified_at')

class ApplicationStatusSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.ApplicationStatus
        fields = ('url', 'uuid', 'text', 'application', 'date', 'order', 'modified_at')

class ApplicationStatusLinkSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.ApplicationStatusLink
        fields = ('url', 'uuid', 'application_status', 'link', 'modified_at')

