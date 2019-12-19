from . import models
import rest_framework_filters as filters
import rest_framework_filters.backends as filter_backends
from rest_framework import serializers

from django.core.exceptions import FieldDoesNotExist
from django.db.models import Q

def generic_ownership_filter_queryset(request, queryset):
    try:
        if not request.user.is_superuser and queryset.model._meta.get_field('user'):
            return queryset.filter(
                Q(user__isnull=True) |
                Q(user__isnull=False) & Q(user=request.user)
            )
    except FieldDoesNotExist:
        pass
    
    return queryset


class LabelFilter(filters.FilterSet):
    class Meta:
        model = models.Label
        fields = {'text': ['exact']}


def company_label_filter_get_queryset(request):
    return generic_ownership_filter_queryset(
        request,
        models.Label.objects.all()
    )


class CompanyFilter(filters.FilterSet):
    labels = filters.RelatedFilter(LabelFilter, field_name='labels', queryset=company_label_filter_get_queryset)

    class Meta:
        model = models.Company
        fields = {}


class OwnershipFilterBackend(filter_backends.RestFrameworkFilterBackend):
    """
    Filter that only allows users to see their own objects, or objects w/o a specific ownership.
    """

    def filter_queryset(self, request, queryset, view):
        queryset = super().filter_queryset(request, queryset, view)

        return generic_ownership_filter_queryset(request, queryset)