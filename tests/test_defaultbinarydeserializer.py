import base64
import unittest

from pyrazine.serdes import DefaultBinaryDeserializer


class TestDefaultBinaryDeserializer(unittest.TestCase):
    def test_mime_type(self):
        deserializer = DefaultBinaryDeserializer(mime_type='application/octet-stream')
        self.assertEqual(deserializer.mime_type, 'application/octet-stream')

    def test_deserialize(self):
        deserializer = DefaultBinaryDeserializer(mime_type='application/octet-stream')

        test_bytes = 'test'.encode('utf-8')
        result = deserializer.deserialize(base64.b64encode(test_bytes).decode('utf-8'))
        self.assertEqual(result, test_bytes)
