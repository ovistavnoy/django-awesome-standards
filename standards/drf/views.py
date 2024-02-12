from typing import List, Dict

from django.http.response import HttpResponseRedirectBase

from rest_framework.response import Response
from rest_framework import generics
from rest_framework import views

from .const import VIEW_SCOPES

__all__ = (
    'StandardAPIViewMixin',
    'StandardListAPIViewMixin',

    'APIView',
    'GenericAPIView',
    'CreateAPIView',
    'ListAPIView',
    'RetrieveAPIView',
    'DestroyAPIView',
    'UpdateAPIView',
    'ListCreateAPIView',
    'RetrieveUpdateAPIView',
    'RetrieveDestroyAPIView',
    'RetrieveUpdateDestroyAPIView',
)


class StandardAPIViewMixin:
    action_name = None
    response_messages = None
    scopes = ()

    def get_response_data(self, response, data) -> Dict:
        result = self._transform_response_data(data)
        messages = self._get_response_messages()
        if messages:
            result['messages'] = messages
        return {
            "code": response.status_code,
            "data": result,
        }

    def _transform_response_data(self, data) -> Dict:
        if VIEW_SCOPES.list not in self.scopes:
            return {'item': data}
        if 'pagination' in data:
            return {
                'items': data.get('items'),
                'pagination': data.get('pagination'),
            }
        return {'items': data}

    def _get_response_messages(self) -> List:
        data = self.get_response_messages()
        if not data:
            return

        assert (
            isinstance(data, (list, tuple))
        ), 'get_response_messages must return list or tuple'
        for item in data:
            assert isinstance(item, dict), 'all response messages must be a dict'
            assert 'title' in item, 'all response messages must have title'
            assert 'text' in item, 'all response messages must have text'
            item.setdefault('type', 'success')
        return data

    def get_response_messages(self) -> List:
        return self.response_messages

    def finalize_response(self, request, response, *args, **kwargs) -> Response:
        redirect_url = None
        if isinstance(response, Response):
            code = str(response.status_code)
            if code.startswith('2'):
                response.data = self.get_response_data(
                    response,
                    response.data
                )

            if code.startswith('3'):
                redirect_url = response.data

        if isinstance(response, HttpResponseRedirectBase):
            redirect_url = response.url

        if redirect_url:
            response = Response(
                self.get_response_data(
                    response,
                    {"redirect": {"location": redirect_url}},
                ),
                status=response.status_code
            )
        return super().finalize_response(request, response, *args, **kwargs)


class StandardListAPIViewMixin(StandardAPIViewMixin):
    pass


class APIView(StandardAPIViewMixin, views.APIView):
    action_name = 'api'
    scopes = ()


class GenericAPIView(StandardAPIViewMixin, generics.GenericAPIView):
    action_name = 'generic'
    scopes = (VIEW_SCOPES.generic, )


class CreateAPIView(StandardAPIViewMixin, generics.CreateAPIView):
    action_name = 'create'
    scopes = (VIEW_SCOPES.generic, VIEW_SCOPES.create)


class ListAPIView(StandardListAPIViewMixin, generics.ListAPIView):
    action_name = 'list'
    scopes = (VIEW_SCOPES.generic, VIEW_SCOPES.list)


class RetrieveAPIView(StandardAPIViewMixin, generics.RetrieveAPIView):
    action_name = 'receive'
    scopes = (VIEW_SCOPES.generic, VIEW_SCOPES.receive)


class DestroyAPIView(StandardAPIViewMixin, generics.DestroyAPIView):
    action_name = 'remove'
    scopes = (VIEW_SCOPES.generic, VIEW_SCOPES.remove)


class UpdateAPIView(StandardAPIViewMixin, generics.UpdateAPIView):
    action_name = 'update'
    scopes = (VIEW_SCOPES.generic, VIEW_SCOPES.update)


class ListCreateAPIView(
    StandardListAPIViewMixin,
    generics.ListCreateAPIView
):
    action_name = 'list_create'
    scopes = (VIEW_SCOPES.generic, VIEW_SCOPES.list, VIEW_SCOPES.create)


class RetrieveUpdateAPIView(
    StandardAPIViewMixin,
    generics.RetrieveUpdateAPIView
):
    action_name = 'receive_update'
    scopes = (VIEW_SCOPES.generic, VIEW_SCOPES.receive, VIEW_SCOPES.update)


class RetrieveDestroyAPIView(
    StandardAPIViewMixin,
    generics.RetrieveDestroyAPIView
):
    action_name = 'receive_remove'
    scopes = (VIEW_SCOPES.generic, VIEW_SCOPES.receive, VIEW_SCOPES.remove)


class RetrieveUpdateDestroyAPIView(
    StandardAPIViewMixin,
    generics.RetrieveUpdateDestroyAPIView
):
    action_name = 'receive_update_remove'
    scopes = (
        VIEW_SCOPES.generic,
        VIEW_SCOPES.receive,
        VIEW_SCOPES.update,
        VIEW_SCOPES.remove,
    )
