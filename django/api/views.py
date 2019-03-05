from django.shortcuts import render
from django.views.generic import TemplateView

# Create your views here.
class ApiHomeView(TemplateView):
    template_name = 'api/api-index.html'