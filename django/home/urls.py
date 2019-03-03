from django.urls import path, include

from . import views

urlpatterns = [
    path('api/', include('restapi.urls')),
    path('', views.HomePageView.as_view(), name='homepage'),
]
