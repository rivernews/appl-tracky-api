import graphene
from graphene_django.types import DjangoObjectType, ObjectType
from graphene_django.filter import DjangoFilterConnectionField
from . import models
from . import filters

# Create GraphQL type

class UserType(DjangoObjectType):
    class Meta:
        model = models.CustomUser

class AddressType(DjangoObjectType):
    class Meta:
        model = models.Address

class LinkType(DjangoObjectType):
    class Meta:
        model = models.Link

class LabelType(DjangoObjectType):
    class Meta:
        model = models.Label

class CompanyNode(DjangoObjectType):
    class Meta:
        model = models.Company
        filterset_class = filters.CompanyFilter
        interfaces = (graphene.relay.Node,)

class CompanyRatingType(DjangoObjectType):
    class Meta:
        model = models.CompanyRating

class ApplicationType(DjangoObjectType):
    class Meta:
        model = models.Application

class PositionLocationType(DjangoObjectType):
    class Meta:
        model = models.PositionLocation

class ApplicationStatusLinkType(DjangoObjectType):
    class Meta:
        model = models.ApplicationStatusLink

class ApplicationStatusType(DjangoObjectType):
    class Meta:
        model = models.ApplicationStatus

# Query
# analog to REST API's routes. Each property is a "route".

class APIQuery(ObjectType):
    company = graphene.relay.Node.Field(CompanyNode)
    companies = DjangoFilterConnectionField(CompanyNode)

class RootQuery(APIQuery, ObjectType):
    pass

schema = graphene.Schema(query=RootQuery)