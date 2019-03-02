from django.shortcuts import render
from django.views import generic

# Create your views here.
class HomePageView(generic.TemplateView):
    template_name = 'home/home.html'

    def get(self, request, *args, **kwargs):
        print("Hey! Home Page View is reached!")
        return super().get(request, *args, **kwargs)