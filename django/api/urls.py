from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.ApiHomeView.as_view(), name='api-homepage'),
]
