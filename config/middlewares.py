import re
import json
from typing import Union
from pydantic import ValidationError
from django.http import HttpResponse
from django.core.handlers.wsgi import WSGIRequest

from config.serializers import InputSerializer


class ValidateInputMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    @classmethod
    def validation_error(cls, error) -> HttpResponse:
        return HttpResponse(status=400, content_type='application/json', content=json.dumps({'detail': error}))

    @classmethod
    def ip_address(cls, request) -> Union[re.Match, None]:
        """ Return Remote IP Address """
        ip = request.META.get('REMOTE_ADDR')
        return re.search(r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$', ip)

    def __call__(self, request: WSGIRequest):
        try:
            self.body = json.loads(request.body or b'{}')
        except json.decoder.JSONDecodeError:
            return self.validation_error('invalid body')

        # IP Validation
        ip = self.ip_address(request)
        if not ip:
            return self.validation_error('invalid ip')

        data = {}

        # Validate Input
        try:
            serialized = InputSerializer(**self.body)
        except ValidationError:
            return self.validation_error('invalid body')

        setattr(request, 'api_auth', serialized.auth)
        setattr(request, 'api_method', serialized.method)
        data = serialized.data
        setattr(request, 'api_data', data or self.body)
        setattr(request, 'remote_ip', ip.string)

        return self.get_response(request)
