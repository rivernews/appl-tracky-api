from django.conf.urls import url, include

from rest_framework import routers
from . import views

from rest_framework_jwt.views import obtain_jwt_token

# REST Framework routes
router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)
router.register(r'addresses', views.AddressViewSet)

urlpatterns = [
    # Django views
    url(r'^home/$', views.ApiHomeView.as_view(), name='api-homepage'),

    # API endpoints
    url(r'^', include(router.urls)),
    
    # social auth endpoints
    # https://github.com/st4lk/django-rest-social-auth/blob/master/rest_social_auth/urls_jwt.py
    url(r'^login/social/$', views.SocialAuthView.as_view(), name='login_social_jwt_user'),

    # login URLs for the browsable API.
    url(r'^login/', include('rest_framework.urls', namespace='rest_framework')),
    
    # JWT token endpoint
    url(r'^api-token-auth/', obtain_jwt_token),
]
