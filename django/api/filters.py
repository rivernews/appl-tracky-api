from . import models
import rest_framework_filters as filters
import rest_framework_filters.backends as filter_backends
from rest_framework import serializers
from django.db.models import Q


class LabelFilter(filters.FilterSet):
    class Meta:
        model = models.Label
        fields = {'text': ['exact']}

def company_label_filter_get_queryset(request):
    if request.user.is_superuser:
        return models.Label.objects.all()
    
    return models.Label.objects.filter(
        Q(user__isnull=True) |
        Q(user__isnull=False) & Q(user=request.user)
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
        if request.user.is_superuser:
            return queryset
        
        return queryset.filter(
            Q(user__isnull=True) |
            Q(user__isnull=False) & Q(user=request.user)
        )