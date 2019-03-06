from django.shortcuts import render
from django.views.generic import TemplateView

from django.contrib.auth import get_user_model
from django.contrib.auth.models import (
    Group,

)
from rest_framework import viewsets
from .serializers import (
    UserSerializer, GroupSerializer,
    
)

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
    serializer_class = UserSerializer

    def get_queryset(self):
        if not self.request.user.is_superuser:
            return get_user_model().objects.filter(uuid=self.request.user.uuid)
        else:
            return get_user_model().objects.all().order_by('-date_joined')


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer