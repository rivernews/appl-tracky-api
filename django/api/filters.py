from . import models
import rest_framework_filters
import rest_framework_filters.backends as filter_backends
from rest_framework import serializers

from django.core.exceptions import FieldDoesNotExist
from django.db.models import Q

from django_filters import OrderingFilter, FilterSet


def ownership_filter_queryset(func):
    def wrapper(*args, **kwargs):
        if len(args) == 1:
            request = args[0]
        elif len(args) > 1:
            request = args[1]
        
        queryset = func(*args, **kwargs)

        # `request` is not guranteed
        # see django-filter doc
        # https://django-filter.readthedocs.io/en/stable/guide/usage.html#request-based-filtering
        if request is None:
            return queryset.none()
        
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


class LabelFilter(rest_framework_filters.FilterSet):
    class Meta:
        model = models.Label
        fields = {'text': ['exact']}


@ownership_filter_queryset
def company_label_filter_get_queryset(request):
    return models.Label.objects.all()

class CompanyFilter(rest_framework_filters.FilterSet):
    labels = rest_framework_filters.RelatedFilter(filterset=LabelFilter, field_name='labels', queryset=company_label_filter_get_queryset)

    class Meta:
        model = models.Company
        fields = {
            'labels': ['isnull']
        }


class OwnershipFilterBackend(filter_backends.RestFrameworkFilterBackend):
    """
    Filter that only allows users to see their own objects, or objects w/o a specific ownership.
    """

    @ownership_filter_queryset
    def filter_queryset(self, request, queryset, view):
        return super().filter_queryset(request, queryset, view)


# Below is for GraphQL


class GraphQLCompanyFilter(FilterSet):
    class Meta:
        model = models.Company
        fields = {
            'labels': ['isnull'],

            # graphene-django uses django-filter, which does not have `RelatedFilter`
            # so we have to explicitly specify relational fields here
            # see SO question (graphene-django not supporting nested filter)
            # https://stackoverflow.com/questions/49326217/graphene-django-nested-filters-relay
            'labels__text': ['exact'],
            
            'name': ['icontains']
        }
    
    order_by = OrderingFilter(fields=(
        ('modified_at',)
    ))
    
    # added for graphene-django
    # because it does not support global filter backend like DRF
    @property
    def qs(self):
        # assume user is already authenticated (login checked)
        # guaranteed this in view
        queryset = super().qs
        if self.request.user.is_superuser:
            return queryset
        return queryset.filter(user=self.request.user)