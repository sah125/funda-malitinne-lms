import json

from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpResponse
from django.test import RequestFactory, SimpleTestCase, override_settings

from core.middleware import UploadSizeLimitMiddleware


class UploadSizeLimitMiddlewareTests(SimpleTestCase):
    @override_settings(MAX_UPLOAD_SIZE=1024 * 1024)
    def test_file_within_limit_is_allowed(self):
        request = RequestFactory().post(
            '/upload/',
            {'file': SimpleUploadedFile('evidence.pdf', b'1' * (1024 * 1024 - 1))},
        )
        middleware = UploadSizeLimitMiddleware(lambda _: HttpResponse('ok'))

        response = middleware(request)

        self.assertEqual(response.status_code, 200)

    @override_settings(MAX_UPLOAD_SIZE=1024 * 1024)
    def test_limit_applies_per_file_not_to_combined_file_size(self):
        request = RequestFactory().post(
            '/upload/',
            {'file': [
                SimpleUploadedFile('first.pdf', b'1' * (600 * 1024)),
                SimpleUploadedFile('second.pdf', b'1' * (600 * 1024)),
            ]},
        )
        middleware = UploadSizeLimitMiddleware(lambda _: HttpResponse('ok'))

        response = middleware(request)

        self.assertEqual(response.status_code, 200)

    @override_settings(MAX_UPLOAD_SIZE=1024 * 1024)
    def test_oversized_api_upload_is_rejected(self):
        request = RequestFactory().post(
            '/api/upload/',
            {'file': SimpleUploadedFile('evidence.pdf', b'1' * (1024 * 1024 + 1))},
        )
        middleware = UploadSizeLimitMiddleware(lambda _: HttpResponse('ok'))

        response = middleware(request)

        self.assertEqual(response.status_code, 413)
        self.assertEqual(
            json.loads(response.content),
            {'error': 'Each uploaded file must be 1 MB or smaller.'},
        )
