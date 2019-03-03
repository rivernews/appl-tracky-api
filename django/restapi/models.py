from django.db import models

# Create your models here.
class Company(models.Model):
    uuid = models.UUIDField()
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    labels = models.ManyToManyField(Label)

    name = models.CharField()
    hq_location = models.OneToOneField('Address', on_delete=models.SET_NULL)
    home_page = models.OneToOneField('Link', on_delete=models.SET_NULL)

    ratings = models.ManyToManyField(CompanyRating)


class Address(models.Model):
    uuid = models.UUIDField()
    place_name = models.CharField()
    country = models.CharField()
    state = models.CharField()
    city = models.CharField()
    street = models.CharField()
    raw_address = models.CharField()
    zipcode = models.CharField()

class Link(models.Model):
    uuid = models.UUIDField()
    name = models.CharField()
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    url = models.URLField()
    value = models.IntegerField()

class Label(models.Model):
    uuid = models.UUIDField()
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    text = models.CharField()
    color = models.CharField()

class CompanyRating(models.Model):
    uuid = models.UUIDField()
    source = models.OneToOneField(Link, on_delete=models.SET_NULL)
    value = models.FloatField()