from . import models
import rest_framework_filters as filters
import rest_framework_filters.backends as filter_backends
from rest_framework import serializers

from django.core.exceptions import FieldDoesNotExist
from django.db.models import Q


def ownership_filter_queryset(func):
    def wrapper(*args, **kwargs):
        if len(args) == 1:
            request = args[0]
        elif len(args) > 1:
            request = args[1]
        
        queryset = func(*args, **kwargs)
        
        try:
            if (not request.user.is_superuser) and queryset.model._meta.get_field('user'):
                return queryset.filter(
                    Q(user__isnull=True) |
                    Q(user__isnull=False) & Q(user=request.user)
                )
        except FieldDoesNotExist:
            pass
        
        return queryset
    
    return wrapper


class LabelFilter(filters.FilterSet):
    class Meta:
        model = models.Label
        fields = {'text': ['exact']}


@ownership_filter_queryset
def company_label_filter_get_queryset(request):
    return models.Label.objects.all()


class CompanyFilter(filters.FilterSet):
    labels = filters.RelatedFilter(LabelFilter, field_name='labels', queryset=company_label_filter_get_queryset)

    class Meta:
        model = models.Company
        fields = {'labels': ['isnull']}


class OwnershipFilterBackend(filter_backends.RestFrameworkFilterBackend):
    """
    Filter that only allows users to see their own objects, or objects w/o a specific ownership.
    """

    @ownership_filter_queryset
    def filter_queryset(self, request, queryset, view):
        return super().filter_queryset(request, queryset, view)