import uuid
from django.db import models
from django.utils import timezone

class ManagedBaseModel(models.Model):
    uuid = models.UUIDField(null=False, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.uuid
    
    class Meta:
        abstract = True

# Create your models here.
class Company(ManagedBaseModel):
    user = models.ForeignKey('User', on_delete=models.CASCADE, null=True) # null to determine if it's pre-populated company or user input company
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
        return self.companyrating_set.filter(company=self).raw('''
            SELECT company_rating_table.*
            FROM 
                restapi_company_rating AS company_rating_table, 
                (
                    SELECT source.text, MAX(sample_date) AS max_sample_date
                    FROM restapi_company_rating
                    GROUP BY source.text
                ) AS latest_ratings_table
            WHERE company_rating_table.source.text = latest_ratings_table.source.text AND company_rating_table.sample_date = latest_ratings_table.max_sample_date
        ''')
    
    @property
    def applications(self):
        return self.application_set.all()
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "companies"
        unique_together = ("user", "name", "home_page")

class CompanyRating(ManagedBaseModel):
    source = models.OneToOneField('Link', on_delete=models.SET_NULL, null=True)
    value = models.FloatField(null=False, blank=False, default=0.0)
    company = models.ForeignKey('Company', on_delete=models.CASCADE, null=False)
    sample_date = models.DateField(null=False, blank=True, default=timezone.now)

    def __str__(self):
        return self.value

class Address(ManagedBaseModel):
    place_name = models.CharField(blank=True, max_length=50)
    country = models.CharField(blank=True, max_length=50)
    state = models.CharField(blank=True, max_length=50)
    city = models.CharField(blank=True, max_length=50)
    street = models.CharField(blank=True, max_length=150)
    raw_address = models.CharField(blank=True, max_length=200)
    zipcode = models.CharField(blank=True, max_length=20)

    def __str__(self):
        return self.place_name or self.raw_address
    
    class Meta:
        verbose_name_plural = "addresses"

class Link(ManagedBaseModel):
    text = models.CharField(blank=False, max_length=200)
    user = models.ForeignKey('User', on_delete=models.CASCADE, null=True) # null to determine if it's pre-populated link or user input link
    url = models.URLField(null=False, blank=False)
    order = models.IntegerField(null=True, blank=True, default=0)

    def __str__(self):
        return self.text

    class Meta:
        ordering = ['-order', 'text']

class Label(ManagedBaseModel):
    user = models.ForeignKey('User', on_delete=models.CASCADE, null=True) # null to determine if it's pre-populated label or user input label
    text = models.CharField(blank=False, max_length=200)
    color = models.CharField(blank=True, max_length=20)
    order = models.IntegerField(null=False, blank=True, default=0)

    def __str__(self):
        return self.text

    class Meta:
        ordering = ['-order', 'text']

class Application(ManagedBaseModel):
    user = models.ForeignKey('User', on_delete=models.CASCADE, null=False)
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

class PositionLocation(ManagedBaseModel):
    application = models.ForeignKey('Application', on_delete=models.CASCADE, null=False)
    location = models.OneToOneField('Address', on_delete=models.CASCADE, null=False, blank=False)

    def __str__(self):
        return str(self.location)

class ApplicationStatus(ManagedBaseModel):
    text = models.CharField(blank=False, max_length=50)
    application = models.ForeignKey('Application', on_delete=models.CASCADE, null=True, blank=False) # null means this status is system pre-populated, instead of user input/defined.
    date = models.DateField(null=True, blank=True, default=timezone.now, help_text="The date this status is updated. You can modify this field to reflect the correct date, especially when you create this status at a later point.")
    order = models.IntegerField(null=False, blank=True, default=0)
    
    @property
    def links(self):
        self.applicationstatuslink_set.all()
    
    def __str__(self):
        return self.text

    class Meta:
        get_latest_by = ['order', 'date', 'created_at']
        verbose_name_plural = "application statuses"

class ApplicationStatusLink(ManagedBaseModel):
    application_status = models.ForeignKey('ApplicationStatus', on_delete=models.CASCADE, null=False)
    link = models.OneToOneField(Link, on_delete=models.CASCADE, null=False, blank=False)

    def __str__(self):
        return str(self.link)