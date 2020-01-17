from django.conf.urls import url

from . import views as SearchViews

urlpatterns = [
    url(r'^es-proxy', SearchViews.ElasticsearchRestApiProxyView.as_view()),
]
