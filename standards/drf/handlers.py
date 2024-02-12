from typing import Dict, List, Iterable

from django.conf import settings
from django.utils.module_loading import import_string
from django.utils.translation import pgettext

from rest_framework.views import exception_handler as drf_exception_handler

__all__ = (
    'ExceptionMessageHandler',
    'default_exception_message_handler',
    'ExceptionHandler',
    'exception_handler',
)

class ExceptionMessageHandler:
    # Code map
    code_invalid= pgettext('standards', 'Invalid input.')
    code_parse_error = pgettext('standards', 'Malformed request.')
    code_authentication_failed = pgettext('standards', 'Incorrect authentication credentials.')
    code_not_authenticated = pgettext('standards', 'Authentication credentials were not provided.')
    code_permission_denied = pgettext('standards', 'You do not have permission to perform this action.')
    code_not_found = pgettext('standards', 'Not found.')
    code_method_not_allowed = pgettext('standards', 'Method "{method}" not allowed.')
    code_not_acceptable = pgettext('standards', 'Could not satisfy the request Accept header.')
    code_unsupported_media_type = pgettext('standards', 'Unsupported media type "{media_type}" in request.')
    code_throttled = pgettext('standards', 'Expected available in {wait} seconds.')
    code_error = pgettext('standards', 'A server error occurred.')

    # Status map
    status_400 = ['invalid', 'parse_error']
    status_401 = ['authentication_failed', 'not_authenticated']
    status_403 = ['permission_denied']
    status_404 = ['not_found']
    status_405 = ['method_not_allowed']
    status_406 = ['not_acceptable']
    status_415 = ['unsupported_media_type']
    status_429 = ['throttled']
    status_500 = ['error']

    def get_code_message(self, code: str):
        return getattr(self, f'code_{code}', None)

    def get_code_range(self, status: int):
        return getattr(self, f'status_{status}', None)

    def __call__(self, status: int, code: str = None, context: Dict={}):
        message = ''
        if code:
            message = self.get_code_message(code)

        code_rande = self.get_code_range(status)
        if not message and code_rande:
            message =  self.get_code_message(code_rande[0])
        return  message.format(**context)

default_exception_message_handler = ExceptionMessageHandler()

CONFIGS = getattr(settings, 'REST_FRAMEWORK', {})
message_handler_path = CONFIGS.get('EXCEPTION_MESSAGE_HANDLER')
exception_message_handler = (
    import_string(message_handler_path)
    if message_handler_path
    else default_exception_message_handler
)


class ExceptionHandler:

    def __call__(self, exc, context):
        self.request = context.get('request')
        self.view = context.get('view')
        self.response = drf_exception_handler(exc, context)
        self.exc = exc
        if self.response is not None and hasattr(exc, 'detail'):
            self.details = self.exc.detail
            self.response.data = self.get_response_data()
        return self.response
        
    def get_response_data(self):
        data = {}
        data['code'] = self.response.status_code
        data['message'] = self.response.status_text
        errors = self.get_errors(self.details) or []
        if errors:
            data['errors'] = [{
                'message': self.get_exception_message(errors),
                'domain': self.get_domain(errors),
                'reason': self.get_exception_reason(errors),
                'state': errors,
            }]
        return data

    def get_exception_message(self, errors: Iterable):
        return exception_message_handler(
            self.response.status_code,
            getattr(self.exc, 'default_code', None),
            {
                'method': self.request.method,
                'media_type': self.request.content_type,
                'wait': self.get_throttle_duration(),
            }
        )

    def get_throttle_duration(self):
        throttle_durations = []
        for throttle in self.view.get_throttles():
            if not throttle.allow_request(self.request, self.view):
                throttle_durations.append(throttle.wait())

        duration = None
        if throttle_durations:
            durations = [
                duration for duration in throttle_durations
                if duration is not None
            ]
            duration = max(durations, default=None)
        return duration

    def get_domain(self, errors: Iterable) -> str:
        return 'request'

    def get_exception_reason(self, errors: Iterable):
        return 'form_value_invalid'

    def get_errors(self, errors, path=None) -> List:
        if isinstance(errors, dict):
            return self.normalize_dict_errors(errors, path)
        elif isinstance(errors, list):
            return self.normalize_list_errors(errors, path)
        else:
            return self.get_error_block(errors)

    def normalize_dict_errors(self, errors: Dict, path=None) -> Dict:
        return {
            field: self.get_errors(error, field)
            for field, error in errors.items()
        }

    def normalize_list_errors(self, errors: List, path=None) -> List:
        return [
            self.get_errors(error)
            for error in errors
        ]

    def get_error_block(self, error) -> Dict:
        return {'message': str(error), 'reason': error.code}


exception_handler = ExceptionHandler()
