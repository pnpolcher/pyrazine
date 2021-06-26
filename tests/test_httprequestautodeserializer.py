from typing import Optional
import unittest

from pyrazine.serdes.auto import HttpRequestAutoDeserializer


class TestHttpRequestAutoDeserializer(unittest.TestCase):

    _deserializer: Optional[HttpRequestAutoDeserializer]

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
        import json

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
