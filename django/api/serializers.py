from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from . import models
from rest_framework import serializers
from rest_social_auth.serializers import UserJWTSerializer

class BaseSerializer(serializers.HyperlinkedModelSerializer):
    uuid = serializers.ReadOnlyField()

class UserSerializer(BaseSerializer):
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

class AddressSerializer(BaseSerializer):
    class Meta:
        model = models.Address
        fields = ('url', 'uuid', 'place_name', 'country', 'state', 'street', 'full_address', 'zipcode', 'modified_at')

class LinkSerializer(BaseSerializer):
    # setup user upon creation, see https://stackoverflow.com/questions/32509815/django-rest-framework-get-data-from-foreign-key-relation
    user = serializers.PrimaryKeyRelatedField(
        # set it to read_only as we're handling the writing part ourselves
        read_only=True,
    )

    class Meta:
        model = models.Link
        fields = ('url', 'uuid', 'text', 'user', 'url', 'order', 'modified_at')

class CompanySerializer(BaseSerializer):
    # setup user upon creation, see https://stackoverflow.com/questions/32509815/django-rest-framework-get-data-from-foreign-key-relation
    user = serializers.PrimaryKeyRelatedField(
        # set it to read_only as we're handling the writing part ourselves
        read_only=True,
    )

    hq_location = AddressSerializer(many=False)
    home_page = LinkSerializer(many=False)

    class Meta:
        model = models.Company
        fields = ('url', 'uuid', 'user', 'labels', 'name', 'hq_location', 'home_page', 'modified_at')
    
    def create(self, validated_data):
        """
            This is the place to create database object in order to store it in database.
            We will only do the object creation part, and return the object.
            Storing to database will be handled by DRF.
        """
        user = validated_data.pop('user')
        hq_location_data = validated_data.pop('hq_location')
        home_page_data = validated_data.pop('home_page')
        hq_location = models.Address.objects.create(**hq_location_data)
        home_page = models.Link.objects.create(**home_page_data, user=user)
        company = models.Company.objects.create(
            **validated_data, 
            # one to one relationship
            hq_location=hq_location, home_page=home_page
        ) 
        return company

class CompanyRatingSerializer(BaseSerializer):
    class Meta:
        model = models.CompanyRating
        fields = ('url', 'uuid', 'source', 'value', 'company', 'sample_date', 'modified_at')

class LabelSerializer(BaseSerializer):
    class Meta:
        model = models.Label
        fields = ('url', 'uuid', 'user', 'text', 'color', 'order', 'modified_at')

class ApplicationSerializer(BaseSerializer):
    class Meta:
        model = models.Application
        fields = (
            'url', 'uuid', 'user', 
            'user_company', 'position_title', 
            'job_description_page', 'job_source', 
            'labels', 'modified_at')

class PositionLocationSerializer(BaseSerializer):
    class Meta:
        model = models.PositionLocation
        fields = ('url', 'uuid', 'application', 'location', 'modified_at')

class ApplicationStatusSerializer(BaseSerializer):
    class Meta:
        model = models.ApplicationStatus
        fields = ('url', 'uuid', 'text', 'application', 'date', 'order', 'modified_at')

class ApplicationStatusLinkSerializer(BaseSerializer):
    class Meta:
        model = models.ApplicationStatusLink
        fields = ('url', 'uuid', 'application_status', 'link', 'modified_at')

