
from django.contrib import admin

from django.contrib.auth.admin import UserAdmin
from api.models import (
    CustomUser, Company, CompanyRating,
    Application, PositionLocation, ApplicationStatus, ApplicationStatusLink,
    Address, Link, Label,
)

def get_all_model_fields(Model):
    return [ field.name for field in Model._meta.fields ]

# Register your models here.
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = get_all_model_fields(CustomUser)

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = get_all_model_fields(Company)

@admin.register(CompanyRating)
class CompanyRatingAdmin(admin.ModelAdmin):
    list_display = get_all_model_fields(CompanyRating)

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = get_all_model_fields(Application)

@admin.register(PositionLocation)
class PositionLocationAdmin(admin.ModelAdmin):
    list_display = get_all_model_fields(PositionLocation)

@admin.register(ApplicationStatus)
class ApplicationStatusAdmin(admin.ModelAdmin):
    list_display = get_all_model_fields(ApplicationStatus)

@admin.register(ApplicationStatusLink)
class ApplicationStatusLinkAdmin(admin.ModelAdmin):
    list_display = get_all_model_fields(ApplicationStatusLink)

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = get_all_model_fields(Address)

@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    list_display = get_all_model_fields(Link)

@admin.register(Label)
class LabelAdmin(admin.ModelAdmin):
    list_display = get_all_model_fields(Label)