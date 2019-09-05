from django.shortcuts import render
from django.views.generic import TemplateView
from django.core.exceptions import FieldDoesNotExist, PermissionDenied

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from . import models
from rest_framework import viewsets
from rest_social_auth.views import SocialJWTUserAuthView
from . import serializers as ApiSerializers

from rest_framework import serializers

from . import permissions as ApiPermissions

from . import utils as ApiUtils

# for health check combining with db migration check
# https://engineering.instawork.com/elegant-database-migrations-on-ecs-74f3487da99f
from django.db import DEFAULT_DB_ALIAS, connections
from django.db.migrations.executor import MigrationExecutor
from django.http import HttpResponse

# Create your views here.
class ApiHomeView(TemplateView):
    template_name = 'api/api-index.html'

    def get(self, request, *arg, **kwargs):
        executor = MigrationExecutor(connections[DEFAULT_DB_ALIAS])
        plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
        if not plan:
            return super().get(request, *arg, **kwargs)
        else:
            print("ERROR: pending database migration exists. Will stop and respond 503, please do the migration first so Django can be ready to serve request.")
            status = 503
            return HttpResponse(status=status)
    
    def get_context_data(self,*args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['is_secure'] = self.request.is_secure()
        context['build_absolute_uri'] = self.request.build_absolute_uri(None)
        context['headers'] = self.request.META

        return context

        


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
        if ApiUtils.is_model_field_exist(self.model, 'user'):
            return self.model.objects.filter(user=self.request.user)
        else:
            return self.model.objects.all()
    
    # def perform_create(self, serializer):
    #     """
    #         After serializer's .is_valid() call:
    #         The create() method of our serializer will now be passed 
    #         an additional 'user' field, along with the validated data from the request.
            
    #         refer to: https://www.django-rest-framework.org/tutorial/4-authentication-and-permissions/
    #     """
    #     if ApiUtils.is_model_field_exist(self.model, 'user'):
    #         serializer.save(user=self.request.user)
    #     else:
    #         serializer.save()

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

    def perform_update(self, serializer):
        """
            At this point when `perform_update()` is called, the subject model's `serializer` already called .is_valid().
            The main goal for `perform_update` is to do serializer.save() to confirm the transaction to database,
            no need to return anything.
        """

        # handles trivial fields and one-to-one fields
        super().perform_create(serializer)

        """
            Below code handles one-to-many fields manually, while using DRF's serializer as much as we can.
            The main goal here is to create related field's serializer, call .is_valid(), and call save()
        """
        # since DRF doesn't handle one-to-many update for us, we need to start from scratch - from request.data, before we call the serializer class.
        data_list = self.request.data.get('applicationstatuslink_set', [])
        list_serializer = ApiSerializers.ApplicationStatusLinkSerializer(
            # appstatuslink_instances_list, 
            serializer.instance.applicationstatuslink_set.all(), 
            data=data_list, 
            many=True, 
            context={'request': self.request},
        )

        # below code will trigger `update()` of the serializer, and commit to database
        if list_serializer.is_valid():
            list_serializer.save(
                user=self.request.user,
                application_status=serializer.instance,
            )
        else:
            raise serializers.ValidationError(str(list_serializer.errors)) 

class ApplicationStatusLinkViewSet(BaseModelViewSet):
    model = models.ApplicationStatusLink
    queryset = models.ApplicationStatusLink.objects.none()
    serializer_class = ApiSerializers.ApplicationStatusLinkSerializer