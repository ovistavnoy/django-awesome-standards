from collections import OrderedDict

from django.http.response import Http404
from django.utils.encoding import force_str

from rest_framework import exceptions, serializers
from rest_framework.metadata import SimpleMetadata
from rest_framework.request import clone_request

__all__ = ('FieldsetMetadata', )


class FieldsetMetadata(SimpleMetadata):
    """
    It returns an ad-hoc set of information about the view.
    Includes filter meta, view extra meta and extended field choices.

    1) Filter metadata available if view has attribute "filterset_class".
    Example:
    ````
    class SomeView(...):
        filterset_class = SomeFilterset
    ```
    
    2) View extra metadata available if view has method "get_extra_meta".
    Example:
    ```
    class SomeView(...):

        def get_extra_meta(self) -> Optional[Dict, List]:
            return {
                'some_field': SomeModelSerializer(
                    SomeModel.objects.all(), many=True
                ).data
            }
    ```

    3) View field choices metadata available if view has method "get_meta_choices".
    Example:
    ```
    class SomeView(...):

        def get_meta_choices(self) -> Dict:
            return {
                'some_field': {
                    'some_key1': 'some_field'               # will get object attribute
                    'some_key2': 'get_some_param'           # will call object method
                    'some_key3': lambda obj: obj.some_attr  # will call lambda with object param
                    'some_key4': self.get_some(obj)         # will call some metod with object param
                }
            }
    ```
    """
    available_actions = ('GET', 'PATCH', 'POST', 'PUT')
    def determine_extra(self, request, view):
        return view.get_extra_meta()

    def determine_filters(self, request, view):
        filters = OrderedDict()
        queryset = view.get_queryset()
        for filter_name, filter_type in view.filterset_class(
            data=request.GET,
            request=request,
            queryset=queryset
        ).filters.items():
            attrs = OrderedDict()
            attrs['label'] = filter_type.label
            attrs['type'] = filter_type.__class__.__name__
            choices = filter_type.extra.get(
                'choices', getattr(filter_type, 'choices', None)
            )
            if choices:
                attrs['choices'] = [
                    {
                        'value': choice_value,
                        'label': force_text(choice_name)
                    }
                    for choice_value, choice_name in choices
                ]

            choice_query = filter_type.extra.get(
                'queryset', getattr(filter_type, 'queryset', None)
            )
            if choice_query:
                attrs['choices'] = [
                    {
                        'value': item.id,
                        'label': force_text(str(item))
                    }
                    for item in choice_query
                ]

            initial = filter_type.extra.get('initial')
            if not initial is None:
                attrs['initial'] = initial
            filters[filter_name] = attrs
        return filters
    
    def determine_metadata(self, request, view):
        self.view = view
        metadata = super().determine_metadata(request, view)

        if hasattr(view, 'filterset_class'):
            metadata['filters'] = self.determine_filters(request, view)

        if hasattr(view, 'get_extra_meta'):
            metadata['extra_meta'] = self.determine_extra(request, view)
        return metadata

    def determine_actions(self, request, view):
        actions = {}
        for method in set(self.available_actions) & set(view.allowed_methods):
            view.request = clone_request(request, method)
            try:
                if hasattr(view, 'check_permissions'):
                    view.check_permissions(view.request)
                if method == 'PUT' and hasattr(view, 'get_object'):
                    view.get_object()
            except (exceptions.APIException, exceptions.PermissionDenied, Http404):
                pass
            else:
                serializer = view.get_serializer()
                actions[method] = self.get_serializer_info(serializer)
            finally:
                view.request = request
        return actions

    def get_field_info(self, field):
        field_info = super().get_field_info(field)
        if field_info.get('read_only'):
            return field_info

        if hasattr(field, 'choices'):
            field_info['choices'] = [
                {
                    'value': choice_value,
                    'label': force_text(choice_name),
                }
                for choice_value, choice_name in field.choices.items()
            ]
        
        if hasattr(field, 'queryset'):
            extra_params = (
                getattr(self.view, 'extra_meta_choices', {})
                .get(field.source, {})
            )

            def get_item_extra(item):
                extra = {}
                for name, key in extra_params.items():
                    value = getattr(item, key, None)
                    extra[name] = value() if callable(value) else value
                return extra

            queryset = getattr(field, 'queryset', [])
            if not hasattr(queryset, '__iter__'):
                queryset = queryset.all()

            field_info['choices'] = [
                {
                    'value': item.id,
                    'label': force_text(str(item)),
                    **get_item_extra(item)
                }
                for item in queryset
            ]
        return field_info
