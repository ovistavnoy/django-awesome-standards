from django.contrib.auth import get_user_model
from django.views.generic import TemplateView
from django.http.response import HttpResponseRedirect

from django_filters.rest_framework.backends import DjangoFilterBackend
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from standards.drf.pagination import pagenumber_pagination, limitoffset_pagination
from standards.drf.views import (
    APIView,
    CreateAPIView,
    ListAPIView,
    RetrieveUpdateAPIView,
)

from .filters import *
from .serializers import *

__all__ = (
    'SomePageView',
    'RedirectView',

    'SomeAPIView',
    'UserListAPIView',
    'UserRetrieveUpdateAPIView',
)

User = get_user_model()


class SomePageView(TemplateView):
    template_name = 'index.jinja'


class SomeAPIView(CreateAPIView):
    permission_classes = (AllowAny, )
    serializer_class = SomeSerializer


class RedirectView(APIView):

    def get(self, request, *args, **kwargs):
        # return HttpResponseRedirect('/1/')
        return Response('/2/', status=302)


class UserListAPIView(ListAPIView):
    filter_backends = (DjangoFilterBackend, )
    filterset_class = SomeFilterSet
    pagination_class = pagenumber_pagination(
        page_size=1,
        max_page_size=2,
    )
    pagination_class = limitoffset_pagination(
        default_limit=1,
        limit_query_param='lim',
    )
    permission_classes = (AllowAny, )
    queryset = User._default_manager.all()
    serializer_class = UserSerializer
    response_messages = [
        {
            'title':'Title 1',
            'text': 'Text 1',
        },
        {
            'title':'Title 2',
            'text': 'Text 2',
            'type': 'some_type',
        },
    ]


class UserRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    permission_classes = (AllowAny, )
    queryset = User._default_manager.all()
    serializer_class = UserSerializer
