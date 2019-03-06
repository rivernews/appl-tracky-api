from django.conf.urls import url, include

from rest_framework import routers
from . import views

from rest_framework_jwt.views import obtain_jwt_token

# REST Framework routes
router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)

urlpatterns = [
    # Django views
    url(r'^$', views.ApiHomeView.as_view(), name='api-homepage'),

    # API endpoints
    url(r'^', include(router.urls)),
    # social auth endpoints
    url(r'^api/login/', include('rest_social_auth.urls_jwt')),

    # login URLs for the browsable API.
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    
    # JWT token endpoint
    url(r'^api-token-auth/', obtain_jwt_token),
]
