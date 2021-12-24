import os
import uuid

from django.http.response import JsonResponse

from django.views.generic import TemplateView

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.utils.encoding import smart_str
from django.conf import settings

from . import models
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_social_auth.views import SocialJWTUserAuthView
from . import serializers as ApiSerializers

from rest_framework import serializers
from rest_framework.permissions import AllowAny

from . import permissions as ApiPermissions

from . import utils as ApiUtils

from . import filters as ApiFilters

# for health check combining with db migration check
# https://engineering.instawork.com/elegant-database-migrations-on-ecs-74f3487da99f
from django.db import DEFAULT_DB_ALIAS, connections
from django.db.migrations.executor import MigrationExecutor
from django.http import HttpResponse

import requests
import boto3

# boto3 S3
# https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html
s3_service = boto3.resource(
    service_name='s3', aws_access_key_id=settings.PRIVATE_IMAGE_AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.PRIVATE_IMAGE_AWS_SECRET_ACCESS_KEY,
    region_name=settings.PRIVATE_IMAGE_AWS_REGION
)

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
        context['context_test_msg'] = 'context passed in message successfully'
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
    filter_class = ApiFilters.CompanyFilter

    def create(self, request):
        return super().create(request)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """
        Serving a PATCH request
        Q: how is update() different from partial_update()?
        A: https://stackoverflow.com/questions/41110742/django-rest-framework-partial-update

        Source code: rest_framework.mixins.UpdateModelMixin
        Additional resources: https://stackoverflow.com/a/37050246/9814131
        """

        """
            1. Sets partial=True
            2. Call viewset.update()
        """

        # detect if it's a batch update or not
        if isinstance(request.data, list):
            # get all instances (db objects) so we can use them to update db
            uuids_to_patch = []
            for partial_company in request.data:
                if not partial_company.get('uuid'):
                    raise Exception('CompanyPathError: PATCH requires at least uuid in the object. Request data is ' + str(request.data)[:1000] + '...')
                uuids_to_patch.append(partial_company['uuid'])

            db_instances = self.get_queryset().filter(uuid__in=uuids_to_patch)

            # create serializer while using partial=True
            list_serializer = ApiSerializers.CompanySerializer(
                db_instances,
                data=self.request.data,
                many=True,
                partial=True,
                context={'request': self.request}
            )

            # validate it
            list_serializer.is_valid(raise_exception=True)

            # pass over to update processes
            self.perform_update(list_serializer)
            return Response(list_serializer.data)

        return super().partial_update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """
            1. Load data into serializer --> permission check
            2. Validate data in serializer --> serializer.validate()
            3. Perform update --> viewset.perform_update()
        """

        return super().update(request, *args, **kwargs)

    def perform_update(self, serializer) -> None:
        """
            1. Serializer commit data change, i.e. serializer.save() --> serializer.update()
        """

        super().perform_update(serializer)

    def perform_create(self, serializer):
        super().perform_create(serializer)



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

# DRF exempts CSRF too - https://stackoverflow.com/questions/51931856/how-does-drf-turn-off-csrf-token-check-for-jwt-based-authentication
# and it only enables CSRF if session auth is used
# JWT does not need CSRF so we can safely disable it here
# there is a debate whether JWT is better than httpOnly cookie (CSRF required) - https://stackoverflow.com/a/52507865/9814131
class PrivateImageView(APIView):
    BUCKET_NAME = settings.PRIVATE_IMAGE_BUCKET_NAME
    FILENAME_LEN_LIMIT = 40

    # we let GET public but not POST. We'll check permission manually in POST view.
    permission_classes = [AllowAny]

    def _get_signed_url(self, key):
        return s3_service.meta.client.generate_presigned_url(
            ClientMethod="get_object", ExpiresIn=600,
            Params={
                "Bucket": self.BUCKET_NAME,
                "Key": key,
            },
        )

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied

        imagefile = request.FILES.get('file')

        # truncate the file name
        imagefilename = imagefile.name
        if '.' in imagefilename:
            *imagefilename_woext, ext = imagefilename.split('.')
            imagefilename_woext = ''.join(imagefilename_woext)
        else:
            imagefilename_woext = imagefilename
            ext = ''
        if len(imagefilename_woext) > self.FILENAME_LEN_LIMIT:
            imagefilename_woext = imagefilename_woext[:self.FILENAME_LEN_LIMIT//2] + '...' + imagefilename_woext[-self.FILENAME_LEN_LIMIT//2:]
            imagefilename = imagefilename_woext
            if ext:
                imagefilename += f'.{ext}'

        # TODO: check file type is image; set size limit
        imagekey = f'{request.user.username}/{uuid.uuid4()}_{imagefilename}'
        s3_service.Bucket(self.BUCKET_NAME).put_object(Key=imagekey, Body=imagefile)

        return JsonResponse({
            'image_url': f'{request.scheme}://{request.get_host()}{request.path}?id={imagekey}'
        }, status=200)

    def get(self, request, *args, **kwargs):
        '''Expects query parameter `?id=username/image/file/path`
        '''

        imagekey = request.GET.get('id', '')
        # TODO: in the future enhance private image security
        # imagekey_username, *_ = imagekey.split('/')
        # if not (request.user.is_authenticated and request.user.username == imagekey_username):
        #     raise PermissionDenied

        url = self._get_signed_url(key=imagekey)

        r = requests.get(url=url, stream=True)
        r.raise_for_status()
        response = HttpResponse(r.raw, content_type='application/force-download')

        filename = os.path.basename(imagekey)
        response['Content-Disposition'] = 'attachment; filename={filename}'.format(filename=smart_str(filename))

        return response
