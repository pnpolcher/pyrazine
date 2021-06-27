from typing import Optional
import unittest

from pyrazine.events import HttpEvent
from pyrazine.serdes.auto import HttpRequestAutoDeserializer


class TestHttpRequestAutoDeserializer(unittest.TestCase):

    _deserializer: Optional[HttpRequestAutoDeserializer]

    def _get_md5_hexdigest(self, b: bytes) -> str:

        from hashlib import md5

        m = md5()
        m.update(b)
        return m.hexdigest()

    def setUp(self) -> None:
        self._deserializer = None

    @property
    def deserializer(self) -> HttpRequestAutoDeserializer:
        if self._deserializer is None:
            self._deserializer = HttpRequestAutoDeserializer.create({})
        return self._deserializer

    def test_create(self):
        self.assertIsInstance(HttpRequestAutoDeserializer.create({}), HttpRequestAutoDeserializer)

    def test_deserialize_json(self):

        from helpers import get_json_payload_event, TEST_JSON_PAYLOAD

        event = get_json_payload_event()
        payload = event.body
        result = self.deserializer.deserialize(payload, parameters={'event': event})
        self.assertTrue(TEST_JSON_PAYLOAD == result)

    def test_deserialize_binary(self):

        from helpers import get_binary_payload_event, TEST_BINARY_PAYLOAD

        event = get_binary_payload_event()
        payload = event.body
        result = self.deserializer.deserialize(payload, parameters={'event': event})
        self.assertEqual(result, TEST_BINARY_PAYLOAD)

    def _test_generic_binary_payload(self, event: HttpEvent, payload_filename: str) -> bool:

        payload = event.body
        result = self.deserializer.deserialize(payload, parameters={'event': event})
        with open(payload_filename, 'rb') as jpeg_file:
            source_digest = self._get_md5_hexdigest(jpeg_file.read())

        target_digest = self._get_md5_hexdigest(result)

        return source_digest == target_digest

    def test_deserialize_jpeg(self):

        from helpers import get_jpeg_payload_event, TEST_JPEG_PAYLOAD_FILE

        event = get_jpeg_payload_event()
        result = self._test_generic_binary_payload(event, TEST_JPEG_PAYLOAD_FILE)

        self.assertTrue(result)

    def test_deserialize_png(self):

        from helpers import get_png_payload_event, TEST_PNG_PAYLOAD_FILE

        event = get_png_payload_event()
        result = self._test_generic_binary_payload(event, TEST_PNG_PAYLOAD_FILE)

        self.assertTrue(result)
