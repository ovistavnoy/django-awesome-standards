from collections import OrderedDict

from rest_framework import pagination
from rest_framework.response import Response

__all__ = (
    'PageNumberPagination',
    'pagenumber_pagination',
    'LimitOffsetPagination',
    'limitoffset_pagination',
)


class StandardPaginationMixin:

    def get_pagination_info(self, data):
        raise NotImplementedError('Method "get_pagination_info" not implemented')

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('items', data),
            ('pagination', self.get_pagination_info(data)),
        ]))

    def get_results(self, data):
        return data.get('items')


class PageNumberPagination(
    StandardPaginationMixin,
    pagination.PageNumberPagination
):
    page_query_param = 'p'

    def get_pagination_info(self, data):
        return {
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'page_size': self.page_size,
        }


def pagenumber_pagination(page_size: int, page_query_param: str='p', **kwargs):
    class Klass(PageNumberPagination):
        def __init__(self, *base_args, **base_kwargs):
            super().__init__(*base_args, **base_kwargs)
            self.page_size = page_size
            self.page_query_param = page_query_param
            for key in kwargs:
                setattr(self, key, kwargs[key])
    return Klass


class LimitOffsetPagination(
    StandardPaginationMixin,
    pagination.LimitOffsetPagination
):

    def get_pagination_info(self, data):
        return  {
            'limit': self.limit,
            'offset': self.offset,
            'total': self.count,
        }

    def paginate_queryset(self, queryset, request, view=None):
        self.count = self.get_count(queryset)
        self.limit = self.get_limit(request)
        self.offset = self.get_offset(request)
        self.request = request

        if not self.limit:
            return list(queryset[self.offset:])

        if self.count > self.limit and self.template is not None:
            self.display_page_controls = True

        if self.count == 0 or self.offset > self.count:
            return []
        return list(queryset[self.offset:self.offset + self.limit])


def limitoffset_pagination(default_limit=None, max_limit=None, **kwargs):
    class Klass(LimitOffsetPagination):
        def __init__(self, *base_args, **base_kwargs):
            super().__init__(*base_args, **base_kwargs)
            self.max_limit = max_limit
            if default_limit:
                self.default_limit = default_limit
            for key in kwargs:
                setattr(self, key, kwargs[key])
    return Klass