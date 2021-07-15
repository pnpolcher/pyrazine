import json
import unittest

from pyrazine.serdes.json import DefaultJSONEncoder, JsonSerializer


class DummyEncoder(json.JSONEncoder):
    pass


class TestJsonSerializer(unittest.TestCase):
    def test_is_base64_encoded(self):
        serializer = JsonSerializer()
        self.assertFalse(serializer.is_base64_encoded)

    def test_mime_type(self):
        serializer = JsonSerializer()
        self.assertEqual(serializer.mime_type, "application/json")

    def test_create(self):
        # Test default
        serializer = JsonSerializer.create({})
        self.assertEqual(serializer._encoder_class, DefaultJSONEncoder)
        self.assertFalse(serializer._json_ld)

        # Test invalid encoder class
        with self.assertRaises(ValueError):
            JsonSerializer.create({'encoder_class': TestJsonSerializer})

        # Test custom parameters
        serializer = JsonSerializer.create({
            'encoder_class': DummyEncoder,
            'variant': 'ld',
        })

        self.assertEqual(serializer._encoder_class, DummyEncoder)
        self.assertTrue(serializer._json_ld)

    def test_serialize(self):
        serializer = JsonSerializer()
