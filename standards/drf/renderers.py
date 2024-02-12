from djangorestframework_camel_case.util import camelize
from drf_orjson_renderer.renderers import ORJSONRenderer

__all__ = ('CamelCaseORJSONRenderer', )


class CamelCaseORJSONRenderer(ORJSONRenderer):

    def render(self, data, *args, **kwargs):
        return super().render(camelize(data), *args, **kwargs)
