import uuid
from django.db import models

class ManagedBaseModel(models.Model):
    uuid = models.UUIDField(null=False, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True

# Create your models here.
class Company(ManagedBaseModel):
    user = models.ForeignKey('User', on_delete=models.CASCADE, null=True) # null to determine if it's pre-populated company or user input company
    labels = models.ManyToManyField(Label, null=True)

    name = models.CharField(blank=False, max_length=100)
    hq_location = models.OneToOneField('Address', on_delete=models.SET_NULL, null=True, blank=True)
    home_page = models.OneToOneField('Link', on_delete=models.SET_NULL, null=True, blank=True)

    ratings = models.ManyToManyField(CompanyRating, null=True, blank=True)


class Address(ManagedBaseModel):
    place_name = models.CharField(blank=True, max_length=50)
    country = models.CharField(blank=True, max_length=50)
    state = models.CharField(blank=True, max_length=50)
    city = models.CharField(blank=True, max_length=50)
    street = models.CharField(blank=True, max_length=150)
    raw_address = models.CharField(blank=True, max_length=200)
    zipcode = models.CharField(blank=True, max_length=20)

class Link(ManagedBaseModel):
    text = models.CharField(blank=False, max_length=200)
    user = models.ForeignKey('User', on_delete=models.CASCADE, null=True) # null to determine if it's pre-populated link or user input link
    url = models.URLField(null=False, blank=False)
    value = models.IntegerField(null=True, blank=True)

class Label(ManagedBaseModel):
    user = models.ForeignKey('User', on_delete=models.CASCADE, null=True) # null to determine if it's pre-populated label or user input label
    text = models.CharField(blank=False, max_length=200)
    color = models.CharField(blank=True, max_length=20)

class CompanyRating(ManagedBaseModel):
    source = models.OneToOneField(Link, on_delete=models.SET_NULL, null=True)
    value = models.FloatField(null=False, blank=False, default=0.0)