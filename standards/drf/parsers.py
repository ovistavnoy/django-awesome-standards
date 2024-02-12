from django.conf import settings
from djangorestframework_camel_case.parser import CamelCaseJSONParser
from djangorestframework_camel_case.util import underscoreize
import orjson
from rest_framework.exceptions import ParseError

__all__ = ('CamelCaseORJSONParser', )


class CamelCaseORJSONParser(CamelCaseJSONParser):

    def parse(self, stream, media_type=None, parser_context=None):
        """
        De-serializes JSON strings to Python objects.

        :param stream: A stream-like object representing the body of the request.
        :param media_type: If provided, this is the media type of the incoming
                request content specified in the `Content-Type` HTTP header.
        :param parser_context: If supplied, this argument will be a dictionary
                containing any additional context that may be required to parse
                the request content.

                By default this will include the following
                keys: view, request, args, kwargs.
        :return: Python native instance of the JSON string.
        """
        parser_context = parser_context or {}
        encoding = parser_context.get("encoding", settings.DEFAULT_CHARSET)

        try:
            data = stream.read().decode(encoding)
            return underscoreize(orjson.loads(data), **self.json_underscoreize)
        except orjson.JSONDecodeError as exc:
            raise ParseError(f"JSON parse error - {exc}")
