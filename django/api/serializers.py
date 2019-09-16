from rest_framework.settings import api_settings

from django.contrib.auth import get_user_model
from django.core.exceptions import FieldDoesNotExist, FieldError
from django.contrib.auth.models import Group
from . import models
from rest_framework import serializers
from rest_social_auth.serializers import UserJWTSerializer

from . import utils as ApiUtils

class BaseSerializer(serializers.HyperlinkedModelSerializer):
    # UUIDField has no allow_blank arg and always enfource a non-blank value, which makes it hard to deal with one-to-many create/update
    # we are using `SlugField` to allow writable related fields, where blank uuid may indicate a `create` request and otherwise `update`.
    # we also cannot use `serializers.ReadOnlyField()` because then uuid will be removed after serializer.is_valid(), and validated_data will have no uuid,
    # but we need uuid in validated_data in order to finish create/update operations.
    uuid = serializers.SlugField(required=False, read_only=False, allow_blank=True)

    """
    one_to_one_fields = [{
        'field_name': None,
        'model': None,
    }, ...]
    """
    one_to_one_fields = {}

    def create(self, validated_data):
        """
            What this function is for:
                After Serializer validated data, define how should object be created.
                You can consider use super().create() to build on the default behavior.
            What to do:
                You will create relational instances manually by `Model.objects.create(...)`,
            What to return:
                Return the created instance.
            
            See https://www.django-rest-framework.org/api-guide/serializers/#writing-create-methods-for-nested-representations

            ** In order to use nested serializer fields, you have to write this .create() function
        """
        
        # create relational objects
        one_to_one_fields_data = self.create_one_to_one_fields(validated_data)

        # remove uuid to avoid writing to uuid field
        # if 'uuid' in validated_data:
        #     del validated_data['uuid']
        
        # include user info whenever possible
        self.inject_user_info_data(self.Meta.model, validated_data)
        
        # create main model obj
        new_model_object = ApiUtils.create_instance(self.Meta.model, {
            **validated_data, **one_to_one_fields_data
        })
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

        # include user info whenever possible
        self.inject_user_info_data(self.Meta.model, validated_data)

        # update subject model instance
        ApiUtils.update_instance(instance, validated_data, self.one_to_one_fields)

        return instance
    
    def update_one_to_one_fields(self, instance, validated_data):
        for field_name, instance_model in self.one_to_one_fields.items():
            if field_name in validated_data and ApiUtils.is_instance_field_exist(instance, field_name):
                # data is provided (and specified by serializer's one_to_one_fields)
                one_to_one_data = validated_data.pop(field_name)

                # include user info if necessary; TODO: we should not need to do this for update; just for debug purpose where previous bug let `user` field blank
                self.inject_user_info_data(instance_model, one_to_one_data)

                # update the one to one field object on instance
                one_to_one_field_instance = getattr(instance, field_name)
                # in case one to one field is null
                if one_to_one_field_instance:
                    # after we update, we don't need to update subject instance since it references to that one to one model
                    ApiUtils.update_instance(one_to_one_field_instance, one_to_one_data)

    def create_one_to_one_fields(self, validated_data):
        one_to_one_fields = {}
        for field_name, instance_model in self.one_to_one_fields.items():

            """
                creating one to one fields
            """

            one_to_one_data = validated_data.pop(field_name)

            # include user info if necessary
            self.inject_user_info_data(instance_model, one_to_one_data)

            # create model object
            one_to_one_fields[field_name] = ApiUtils.create_instance(instance_model, one_to_one_data)
            
        return one_to_one_fields
    
    def inject_user_info_data(self, model, one_to_one_data):
        if ApiUtils.is_model_field_exist(model, 'user'):
                request = self.context.get('request', None)
                if request:
                    if request.user.is_authenticated:
                        one_to_one_data['user'] = request.user
                    else:
                        raise FieldError('One to one field object requires a user field, but user is not authenticated. Please make sure you login.')
    
    class Meta:
        model = None
        fields = (api_settings.URL_FIELD_NAME, 'uuid', 'modified_at')

class UserSerializer(BaseSerializer):
    """
    For general API endpoint
    """
    class Meta:
        model = get_user_model()
        fields = (api_settings.URL_FIELD_NAME, 'email', 'first_name', 'last_name')


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
        fields = (api_settings.URL_FIELD_NAME, 'name')

"""
    Main Data Model
"""

class AddressSerializer(BaseSerializer):
    class Meta:
        model = models.Address
        fields = ('place_name', 'country', 'state', 'street', 'full_address', 'zipcode') + BaseSerializer.Meta.fields

class LinkSerializer(BaseSerializer):
    # setup user upon creation, see https://stackoverflow.com/questions/32509815/django-rest-framework-get-data-from-foreign-key-relation
    user = serializers.PrimaryKeyRelatedField(
        # set it to read_only as we're handling the writing part ourselves
        read_only=True,
    )

    class Meta:
        model = models.Link
        fields = ('text', 'user', 'url', 'order') + BaseSerializer.Meta.fields

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
        fields = ('user', 'labels', 'name', 'hq_location', 'home_page') + BaseSerializer.Meta.fields
    
class CompanyRatingSerializer(BaseSerializer):

    source = LinkSerializer(many=False)
    
    company = serializers.PrimaryKeyRelatedField(read_only=False, queryset=models.Company.objects.all())

    one_to_one_fields = {
        'source': models.Link,
    }

    class Meta:
        model = models.CompanyRating
        fields = ('source', 'value', 'company', 'sample_date') + BaseSerializer.Meta.fields

class LabelSerializer(BaseSerializer):
    class Meta:
        model = models.Label
        fields = ('user', 'text', 'color', 'order') + BaseSerializer.Meta.fields

class ApplicationSerializer(BaseSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True) # foreign jey

    # foreign key & frontend use uuid to specify (write to this field) the target company
    # the `queryset=...` arg is for lookup the company obj by uuid from frontend
    user_company = serializers.PrimaryKeyRelatedField(read_only=False, required=False, queryset=models.Company.objects.all())

    job_description_page = LinkSerializer(many=False) # onetoone
    job_source = LinkSerializer(many=False) # onetoone

    one_to_one_fields = {
        'job_description_page': models.Link,
        'job_source': models.Link,
    }

    class Meta:
        model = models.Application
        fields = (
            'user', 
            'user_company', 'position_title', 
            'job_description_page', 'job_source', 
            'labels', 'notes') + BaseSerializer.Meta.fields
    
class PositionLocationSerializer(BaseSerializer):

    location = AddressSerializer(many=False)

    application = serializers.PrimaryKeyRelatedField(read_only=False, queryset=models.Application.objects.all())

    one_to_one_fields = {
        'location': models.Address,
    }

    class Meta:
        model = models.PositionLocation
        fields = ('application', 'location') + BaseSerializer.Meta.fields


class ApplicationStatusLinkListSerializer(serializers.ListSerializer):
    
    def update(self, instance, validated_data, **kwargs):
        """
            This ListSerializer is an instruction of when given a list of application status link instances,
            how we should call `ApplicationStatusLinkSerializer(...)`.

            We do best effort when dealing with update of multiple instances(=objects):
            If the object is not in our database - we interpret this as a create request
            If the object is in our database - we interpret it as update
            If an object is in our database, more specifically, within the reverse foreign key set, but not provided from the frontend, 
            we interpret this as a delete request
        """

        # pull out the entire reverse foreign key set, so when an object is missing, we know what to delete
        all_instance_table = { str(in_db_instance.uuid): in_db_instance for in_db_instance in instance }

        update_data_table = { update_instance_data['uuid']: update_instance_data for update_instance_data in validated_data }

        # handle update or create
        update_data_uuids = list(update_data_table.keys())
        update_instances = []
        for data_uuid in update_data_uuids:
            
            # update - object is in both database and frontend form data
            if data_uuid in all_instance_table:
                target_data = update_data_table.pop(data_uuid)
                target_update_instance = all_instance_table.pop(data_uuid)
                update_instance = self.child.update(
                    target_update_instance,
                    target_data
                )
                update_instances.append(update_instance)

            # create - object is not in database, but frontend form sends it over here
            else:
                target_data = update_data_table.pop(data_uuid)
                created_instance = self.child.create(target_data)
                update_instances.append(created_instance)

        # handle delete
        for data_uuid, instance_to_delete in all_instance_table.items():
            instance_to_delete.delete()

        return update_instances


class ApplicationStatusLinkSerializer(BaseSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True,)
    link = LinkSerializer(many=False, read_only=False)
    application_status = serializers.PrimaryKeyRelatedField(read_only=True)

    one_to_one_fields = {
        "link": models.Link
    }

    class Meta:
        model = models.ApplicationStatusLink
        fields = ('application_status', 'link', 'user') + BaseSerializer.Meta.fields

        # when using `many=True` on ApplicationStatusLinkSerializer(many=True), will use the following class for deserialize
        list_serializer_class = ApplicationStatusLinkListSerializer


class ApplicationStatusSerializer(BaseSerializer):

    application = serializers.PrimaryKeyRelatedField(read_only=False, queryset=models.Application.objects.all())
    applicationstatuslink_set = ApplicationStatusLinkSerializer(many=True, read_only=False, required=False)

    class Meta:
        model = models.ApplicationStatus
        fields = (
            'text', 'application', 'date', 'order', 
            
            # computed properties
            'applicationstatuslink_set', 
        ) + BaseSerializer.Meta.fields

    def create(self, validated_data):
        new_application_status = ApiUtils.create_instance(
            models.ApplicationStatus,
            validated_data
        )
        # new_application_status = models.ApplicationStatus.objects.create(
        #     text=validated_data.pop('text'), 
        #     application=validated_data.pop('application'), 
        #     date=validated_data.pop('date'),
        #     order=validated_data.get('date', '')
        # )

        application_status_links_data_list = validated_data.pop('applicationstatuslink_set')
        for application_status_link_data in application_status_links_data_list:
            # create link obj
            new_link = ApiUtils.create_instance(
                models.Link,
                {
                    **application_status_link_data['link'],
                    'user': new_application_status.application.user,
                },
            )
            # create application status link obj
            new_application_status_link = ApiUtils.create_instance(
                models.ApplicationStatusLink,
                {
                    'link': new_link,
                    'application_status': new_application_status,
                    'user': new_application_status.application.user,
                }
            )
        
        
        return new_application_status