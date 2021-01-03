import graphene
from graphene_django.types import DjangoObjectType, ObjectType
from graphene_django.filter import DjangoFilterConnectionField
from . import models
from . import filters

# Create GraphQL type

class PaginationConnection(graphene.relay.Connection):
    class Meta:
        abstract = True
    
    # refer to issue
    # https://github.com/graphql-python/graphene-django/issues/636#issuecomment-492031448
    # this is the offical recommended way - add it (total_count, etc) yourself
    # see https://github.com/graphql-python/graphene/issues/307
    # graphql spec on pagination
    # https://graphql.org/learn/pagination/

    totalCount = graphene.Int()
    def resolve_totalCount(root, info):
        return root.length
    
    count = graphene.Int()
    def resolve_count(root, info):
        return len(root.edges)

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

class CompanyRatingType(DjangoObjectType):
    class Meta:
        model = models.CompanyRating

class ApplicationType(DjangoObjectType):
    class Meta:
        model = models.Application

class CompanyNode(DjangoObjectType):
    applications = graphene.List(ApplicationType)
    class Meta:
        model = models.Company
        filterset_class = filters.GraphQLCompanyFilter
        connection_class = PaginationConnection
        interfaces = (graphene.relay.Node,)
    
    def resolve_applications(root, info):
        return root.applications.all()

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

schema = graphene.Schema(query=RootQuery, auto_camelcase=False)