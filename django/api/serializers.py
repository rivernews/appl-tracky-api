from django.contrib.auth import get_user_model
from django.core.exceptions import FieldDoesNotExist
from django.contrib.auth.models import Group
from . import models
from rest_framework import serializers
from rest_social_auth.serializers import UserJWTSerializer

class BaseSerializer(serializers.HyperlinkedModelSerializer):
    uuid = serializers.ReadOnlyField()

    """
    one_to_one_fields = [{
        'field_name': None,
        'model': None,
    }, ...]
    """
    one_to_one_fields = []

    def create(self, validated_data):
        """
            In order to use nested serializer fields, you have to write this .create() function
        """
        additional_fields = {}
        
        # handle optional user field for model
        model_user_field_data = validated_data.get('user', None)
        try:
            self.Meta.model._meta.get_field('user')
            is_model_user_field_exist = True
        except FieldDoesNotExist:
            is_model_user_field_exist = False

        # access data
        for one_to_one_field in self.one_to_one_fields:
            field_name = one_to_one_field['field_name']
            model = one_to_one_field['model']
            try:
                model._meta.get_field('user')
                is_user_field_exist = True
            except FieldDoesNotExist:
                is_user_field_exist = False

            # create model object
            data = validated_data.pop(field_name)
            if model_user_field_data and is_user_field_exist:
                data = { **data, 'user': model_user_field_data }
            additional_fields[field_name] = model.objects.create(**data)

        # create main model obj
        new_model_object = self.Meta.model.objects.create(
            **validated_data, **additional_fields
        )
        return new_model_object
    
    class Meta:
        model = None

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

    one_to_one_fields = [
        {
            'field_name': 'hq_location',
            'model': models.Address,
        },
        {
            'field_name': 'home_page',
            'model': models.Link,
        },
    ]

    class Meta:
        model = models.Company
        fields = ('url', 'uuid', 'user', 'labels', 'name', 'hq_location', 'home_page', 'modified_at')
    
class CompanyRatingSerializer(BaseSerializer):

    source = LinkSerializer(many=False)
    
    company = serializers.PrimaryKeyRelatedField(read_only=False, queryset=models.Company.objects.all())

    one_to_one_fields = [
        {
            'field_name': 'source',
            'model': models.Link,
        },
    ]

    class Meta:
        model = models.CompanyRating
        fields = ('url', 'uuid', 'source', 'value', 'company', 'sample_date', 'modified_at')

class LabelSerializer(BaseSerializer):
    class Meta:
        model = models.Label
        fields = ('url', 'uuid', 'user', 'text', 'color', 'order', 'modified_at')

class ApplicationSerializer(BaseSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True) # foreign jey

    # foreign key & frontend use uuid to specify (write to this field) the target company
    # the `queryset=...` arg is for lookup the company obj by uuid from frontend
    user_company = serializers.PrimaryKeyRelatedField(read_only=False, queryset=models.Company.objects.all())

    job_description_page = LinkSerializer(many=False) # onetoone
    job_source = LinkSerializer(many=False) # onetoone

    one_to_one_fields = [
        {
            'field_name': 'job_description_page',
            'model': models.Link,
        },
        {
            'field_name': 'job_source',
            'model': models.Link,
        },
    ]

    class Meta:
        model = models.Application
        fields = (
            'url', 'uuid', 'user', 
            'user_company', 'position_title', 
            'job_description_page', 'job_source', 
            'labels', 'modified_at')
    
class PositionLocationSerializer(BaseSerializer):

    location = AddressSerializer(many=False)

    application = serializers.PrimaryKeyRelatedField(read_only=False, queryset=models.Application.objects.all())

    one_to_one_fields = [
        {
            'field_name': 'location',
            'model': models.Address,
        },
    ]

    class Meta:
        model = models.PositionLocation
        fields = ('url', 'uuid', 'application', 'location', 'modified_at')

class ApplicationStatusSerializer(BaseSerializer):

    application = serializers.PrimaryKeyRelatedField(read_only=False, queryset=models.Application.objects.all())

    class Meta:
        model = models.ApplicationStatus
        fields = (
            'url', 'uuid', 'text', 'application', 'date', 'order', 'modified_at', 
            
            # computed properties
            'application_status_links'
        )

class ApplicationStatusLinkSerializer(BaseSerializer):

    link = LinkSerializer(many=False)

    application_status = serializers.PrimaryKeyRelatedField(read_only=False, queryset=models.ApplicationStatus.objects.all())

    one_to_one_fields = [
        {
            'field_name': 'link',
            'model': models.Link,
        },
    ]

    class Meta:
        model = models.ApplicationStatusLink
        fields = ('url', 'uuid', 'application_status', 'link', 'modified_at')

