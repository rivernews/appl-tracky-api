import uuid

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser

from django.utils import timezone

from django.dispatch import receiver
from django.db.models.signals import post_delete

class CustomUser(AbstractUser):
    # add additional fields in here
    uuid = models.UUIDField(primary_key=True, blank=True, default=uuid.uuid4)
    avatar_url = models.URLField(null=True, blank=True)

    REQUIRED_FIELDS = ['email', 'first_name', 'last_name'] # will prompt these when do createsuperuser

    def __init__(self, *args, **kwargs):
        self._meta.get_field('email').blank = False # alter the value in AbstractUser w/o additional settings: https://stackoverflow.com/questions/45722025/forcing-unique-email-address-during-registration-with-django
        self._meta.get_field('email')._unique = True
        self._meta.get_field('first_name').blank = False
        self._meta.get_field('last_name').blank = False
        super(CustomUser, self).__init__(*args, **kwargs)
    
    def __str__(self):
        return self.email
    
    class Meta:
        ordering = ['-date_joined', 'first_name', 'last_name']

class ManagedBaseModel(models.Model):
    uuid = models.UUIDField(primary_key=True, null=False, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.uuid
    
    class Meta:
        abstract = True
        ordering = ['created_at']

class Address(ManagedBaseModel):
    place_name = models.CharField(blank=True, max_length=50)
    country = models.CharField(blank=True, max_length=50)
    state = models.CharField(blank=True, max_length=50)
    city = models.CharField(blank=True, max_length=50)
    street = models.CharField(blank=True, max_length=150)
    full_address = models.CharField(blank=True, max_length=200, help_text="The full address of the form does not apply for your address.")
    zipcode = models.CharField(blank=True, max_length=20)

    def __str__(self):
        return self.place_name or self.full_address
    
    class Meta(ManagedBaseModel.Meta):
        verbose_name_plural = "addresses"

class Link(ManagedBaseModel):
    text = models.CharField(blank=True, max_length=200)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True, blank=True) # null to determine if it's pre-populated link or user input link
    url = models.URLField(null=True, blank=True)
    order = models.IntegerField(null=True, blank=True, default=0)

    def __str__(self):
        return self.text

    class Meta(ManagedBaseModel.Meta):
        ordering = ['-order', 'text', 'url']

class Label(ManagedBaseModel):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True) # null to determine if it's pre-populated label or user input label
    text = models.CharField(blank=False, max_length=200)
    color = models.CharField(blank=True, max_length=20)
    order = models.IntegerField(null=False, blank=True, default=0)

    # you can use label.company_set or label.application_set to do reverse lookup

    def __str__(self):
        return self.text

    class Meta(ManagedBaseModel.Meta):
        ordering = ['-order', 'text']
        
class Company(ManagedBaseModel):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True, blank=True) # null to determine if it's pre-populated company or user input company
    labels = models.ManyToManyField('Label', blank=True)

    name = models.CharField(blank=False, max_length=100)
    hq_location = models.OneToOneField('Address', on_delete=models.SET_NULL, null=True, blank=True)
    home_page = models.OneToOneField('Link', on_delete=models.SET_NULL, null=True, blank=True)

    @property
    def ratings(self):
        return self.companyrating_set.all()
    
    # https://stackoverflow.com/questions/7020313/filtering-django-query-by-the-record-with-the-maximum-column-value
    @property
    def latest_ratings(self):
        return self.companyrating_set.filter(company=self).raw(f'''
            SELECT company_rating_table.*
            FROM 
                %s AS company_rating_table, 
                (
                    SELECT source.text, MAX(sample_date) AS max_sample_date
                    FROM %s
                    GROUP BY source.text
                ) AS latest_ratings_table
            WHERE company_rating_table.source.text = latest_ratings_table.source.text AND company_rating_table.sample_date = latest_ratings_table.max_sample_date
        ''', [CompanyRating.objects.model._meta.db_table] * 2) # https://stackoverflow.com/questions/23404551/django-get-table-name-of-a-model-in-the-model-manager/23405140
    
    @property
    def applications(self):
        return self.application_set.all()
    
    def __str__(self):
        return self.name
    
    class Meta(ManagedBaseModel.Meta):
        verbose_name_plural = "companies"
        unique_together = ("user", "name", "home_page")

@receiver(post_delete, sender=Company)
def post_delete_company_onetoone_fields(sender, instance, *args, **kwargs):
    """
        https://stackoverflow.com/questions/12754024/onetoonefield-and-deleting
    """
    if instance.hq_location:
        instance.hq_location.delete()
    if instance.home_page:
        instance.home_page.delete()

class CompanyRating(ManagedBaseModel):
    source = models.OneToOneField('Link', on_delete=models.SET_NULL, null=True)
    value = models.FloatField(null=False, blank=False, default=0.0)
    company = models.ForeignKey('Company', on_delete=models.CASCADE, null=False)
    sample_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.value
    
    class Meta(ManagedBaseModel.Meta):
        pass

@receiver(post_delete, sender=CompanyRating)
def post_delete_companyrating_onetoone_fields(sender, instance, *args, **kwargs):
    if instance.source:
        instance.source.delete()

class Application(ManagedBaseModel):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=False)
    user_company = models.ForeignKey('Company', on_delete=models.CASCADE, null=True)

    @property
    def latest_status(self):
        return self.applicationstatus_set.latest()
    
    @property
    def statuses(self):
        return self.applicationstatus_set.all()

    position_title = models.CharField(blank=False, max_length=150)
    @property
    def position_locations(self):
        return self.positionlocation_set.all()

    job_description_page = models.OneToOneField('Link', related_name="job_description_page_application", on_delete=models.SET_NULL, null=True, blank=True, help_text="The page describing qualifications and responsibilities of the position.")
    job_source = models.OneToOneField('Link', related_name="job_source_application", on_delete=models.SET_NULL, null=True, blank=True, help_text="Specify where do you hear this position, e.g. Handshake, Linkedin, Glassdoor..., etc.")

    labels = models.ManyToManyField('Label', blank=True)

    def __str__(self):
        return self.position_title
    
    class Meta(ManagedBaseModel.Meta):
        pass

@receiver(post_delete, sender=Application)
def post_delete_application_onetoone_fields(sender, instance, *args, **kwargs):
    if instance.job_description_page:
        instance.job_description_page.delete()
    if instance.job_source:
        instance.job_source.delete()

class PositionLocation(ManagedBaseModel):
    application = models.ForeignKey('Application', on_delete=models.CASCADE, null=False)
    location = models.OneToOneField('Address', on_delete=models.CASCADE, null=False, blank=False)

    def __str__(self):
        return str(self.location)
    
    class Meta(ManagedBaseModel.Meta):
        pass

@receiver(post_delete, sender=PositionLocation)
def post_delete_positionlocation_onetoone_fields(sender, instance, *args, **kwargs):
    if instance.location:
        instance.location.delete()

class ApplicationStatusLink(ManagedBaseModel):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True, blank=True)
    application_status = models.ForeignKey('ApplicationStatus', on_delete=models.CASCADE, null=True) # we will set this at a later point when ApplicationStatus obj is created
    link = models.OneToOneField(Link, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return str(self.link)
    
    class Meta(ManagedBaseModel.Meta):
        pass

@receiver(post_delete, sender=ApplicationStatusLink)
def post_delete_applicationstatuslink_onetoone_fields(sender, instance, *args, **kwargs):
    if instance.link:
        instance.link.delete()

class ApplicationStatus(ManagedBaseModel):
    text = models.CharField(blank=False, max_length=50)
    application = models.ForeignKey('Application', on_delete=models.CASCADE, null=True, blank=True) # null means this status is system pre-populated, instead of user input/defined.
    date = models.DateField(null=True, blank=True, default=timezone.localdate, help_text="The date this status is updated. You can modify this field to reflect the correct date, especially when you create this status at a later point.")
    order = models.IntegerField(null=False, blank=True, default=0)
    
    def __str__(self):
        return self.text

    class Meta(ManagedBaseModel.Meta):
        get_latest_by = ['order', 'date', 'created_at']
        verbose_name_plural = "application_statuses"

