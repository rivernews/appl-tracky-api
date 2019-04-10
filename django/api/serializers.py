from django.contrib.auth import get_user_model
from django.core.exceptions import FieldDoesNotExist, FieldError
from django.contrib.auth.models import Group
from . import models
from rest_framework import serializers
from rest_social_auth.serializers import UserJWTSerializer

from . import utils as ApiUtils

class BaseSerializer(serializers.HyperlinkedModelSerializer):
    uuid = serializers.ReadOnlyField()

    """
    one_to_one_fields = [{
        'field_name': None,
        'model': None,
    }, ...]
    """
    one_to_one_fields = {}
    model_user_field_data = None

    def create(self, validated_data):
        """
            In order to use nested serializer fields, you have to write this .create() function
        """
        # handle optional user field for model
        self.model_user_field_data = validated_data.get('user', None)

        # create relational objects
        relational_fields = self.create_one_to_one_fields(validated_data)

        # create main model obj
        new_model_object = self.Meta.model.objects.create(
            **validated_data, **relational_fields
        )
        return new_model_object
    
    def update(self, instance, validated_data):
        """
            Update function is a best effort base service.
            It will try to update the field available.
            If there's a mismatch between data provided and data model schema,
            it will ignore them.

            Particularly, it will handle one-to-one fields
        """
        self.update_one_to_one_fields(instance, validated_data)
        ApiUtils.update_instance(instance, validated_data, self.one_to_one_fields)

        return instance
    
    def update_one_to_one_fields(self, instance, validated_data):

        for field_name, model in self.one_to_one_fields.items():
            if field_name in validated_data and ApiUtils.is_instance_field_exist(instance, field_name):
                # data is provided (and specified by serializer's one_to_one_fields)
                one_to_one_data = validated_data.pop(field_name)

                # update the one to one field object on instance
                one_to_one_field_instance = getattr(instance, field_name)
                # in case one to one field is null
                if one_to_one_field_instance:
                    # after we update, we don't need to update subject instance since it references to that one to one model
                    ApiUtils.update_instance(one_to_one_field_instance, one_to_one_data)

    
    def create_one_to_one_fields(self, validated_data):
        one_to_one_fields = {}
        for field_name, model in self.one_to_one_fields.items():

            """
                creating one to one fields
            """

            one_to_one_data = validated_data.pop(field_name)

            # include user info if necessary
            is_user_field_exist = ApiUtils.is_model_field_exist(model, 'user')
            if self.model_user_field_data and is_user_field_exist:
                one_to_one_data = { **one_to_one_data, 'user': self.model_user_field_data }
            elif (not self.model_user_field_data) and is_user_field_exist:
                raise FieldError('One to one field object requires a user field, but no user info provided. Please make sure you login.')

            # create model object
            one_to_one_fields[field_name] = model.objects.create(**one_to_one_data)
            
        return one_to_one_fields
    
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

    one_to_one_fields = {
        'hq_location': models.Address,
        'home_page': models.Link,
    }

    class Meta:
        model = models.Company
        fields = ('url', 'uuid', 'user', 'labels', 'name', 'hq_location', 'home_page', 'modified_at')
    
class CompanyRatingSerializer(BaseSerializer):

    source = LinkSerializer(many=False)
    
    company = serializers.PrimaryKeyRelatedField(read_only=False, queryset=models.Company.objects.all())

    one_to_one_fields = {
        'source': models.Link,
    }

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

    one_to_one_fields = {
        'job_description_page': models.Link,
        'job_source': models.Link,
    }

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

    one_to_one_fields = {
        'location': models.Address,
    }

    class Meta:
        model = models.PositionLocation
        fields = ('url', 'uuid', 'application', 'location', 'modified_at')


class ApplicationStatusLinkSerializer(BaseSerializer):

    link = LinkSerializer(many=False)
    application_status = serializers.PrimaryKeyRelatedField(read_only=True)

    one_to_one_fields = {
        "link": models.Link
    }

    class Meta:
        model = models.ApplicationStatusLink
        fields = ('url', 'uuid', 'application_status', 'link', 'modified_at')


class ApplicationStatusSerializer(BaseSerializer):

    application = serializers.PrimaryKeyRelatedField(read_only=False, queryset=models.Application.objects.all())
    applicationstatuslink_set = ApplicationStatusLinkSerializer(many=True, read_only=False)

    class Meta:
        model = models.ApplicationStatus
        fields = (
            'url', 'uuid', 'text', 'application', 'date', 'order', 'modified_at', 
            
            # computed properties
            # 'application_status_links'
            'applicationstatuslink_set'
        )

    def create(self, validated_data):
        
        new_application_status = models.ApplicationStatus.objects.create(
            text=validated_data.pop('text'), 
            application=validated_data.pop('application'), 
            date=validated_data.pop('date')
        )

        application_status_links_data_list = validated_data.pop('applicationstatuslink_set')
        for application_status_link_data in application_status_links_data_list:
            # create link obj
            new_link = models.Link.objects.create(**{
                **application_status_link_data['link'],
                'user': new_application_status.application.user,
            })

            # create application status link obj
            new_application_status_link = models.ApplicationStatusLink.objects.create(**{
                'link': new_link,
                'application_status': new_application_status,
                'user': new_application_status.application.user,
            })

        return new_application_status