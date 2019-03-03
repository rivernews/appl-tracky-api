from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.ApiHomeView.as_view(), name='api-homepage'),
]
