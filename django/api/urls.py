from django.conf.urls import url, include

from rest_framework import routers
from . import views

from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token

# REST Framework routes
router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)
# REST API
router.register(r'companies', views.CompanyViewSet)
router.register(r'company-ratings', views.CompanyRatingViewSet)
router.register(r'addresses', views.AddressViewSet)
router.register(r'links', views.LinkViewSet)
router.register(r'labels', views.LabelViewSet)
router.register(r'applications', views.ApplicationViewSet)
router.register(r'position-locations', views.PositionLocationViewSet)
router.register(r'application-statuses', views.ApplicationStatusViewSet)
router.register(r'application-status-links', views.ApplicationStatusLinkViewSet)

urlpatterns = [
    # Django views
    url(r'^$', views.ApiHomeView.as_view(), name='homepage'),
    url(r'^home/$', views.ApiHomeView.as_view(), name='homepage-home'),
    url(r'^health-check', views.ApiHomeView.as_view(), name='homepage-home'),

    # social auth endpoints
    # https://github.com/st4lk/django-rest-social-auth/blob/master/rest_social_auth/urls_jwt.py
    url(r'^api/login/social/$', views.SocialAuthView.as_view(), name='login_social_jwt_user'),

    # login URLs for the browsable API.
    url(r'^login/', include('rest_framework.urls', namespace='rest_framework')),
    
    # JWT token endpoint
    url(r'^api/api-token-auth/', obtain_jwt_token),
    url(r'^api/api-token-refresh/', refresh_jwt_token),

    # API endpoints
    url(r'^api/', include(router.urls)),
]
