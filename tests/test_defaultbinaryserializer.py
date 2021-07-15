import base64
import struct
import sys
import unittest

from pyrazine.serdes.binary import DefaultBinarySerializer


class TestDefaultBinarySerializer(unittest.TestCase):

    def test_is_base_64_encoded(self):

        serializer = DefaultBinarySerializer()
        self.assertTrue(serializer.is_base64_encoded)

    def test_mime_type(self):

        # Test default value
        serializer = DefaultBinarySerializer()
        self.assertEqual(serializer.mime_type, "application/octet-stream")

        # Test custom value
        serializer = DefaultBinarySerializer(mime_type='image/jpeg')
        self.assertEqual(serializer.mime_type, 'image/jpeg')

    def test_create(self):

        # Test default parameters.
        serializer = DefaultBinarySerializer.create({})
        self.assertEqual(serializer._byteorder, 'little')
        self.assertEqual(serializer._int_length, sys.int_info.sizeof_digit)
        self.assertFalse(serializer._int_signed)
        self.assertEqual(serializer.mime_type, 'application/octet-stream')

        # Test custom parameters.
        serializer = DefaultBinarySerializer.create({
            'byteorder': 'big',
            'int_length': 8,
            'int_signed': True,
            'mime_type': 'image/jpeg'
        })

        self.assertEqual(serializer._byteorder, 'big')
        self.assertEqual(serializer._int_length, 8)
        self.assertTrue(serializer._int_signed)
        self.assertEqual(serializer.mime_type, 'image/jpeg')

    def test_serialize_dict(self):
        serializer = DefaultBinarySerializer()

        result = serializer.serialize({}, {})
        self.assertEqual(result, base64.b64encode('{}'.encode('utf-8')))

    def test_serializer_float(self):
        serializer = DefaultBinarySerializer()

        result = serializer.serialize(1.0, {})
        self.assertEqual(result, base64.b64encode(struct.pack('f', 1.0)))

    def test_serializer_int(self):
        serializer = DefaultBinarySerializer()

        result = serializer.serialize(1, {})
        self.assertEqual(result, base64.b64encode())

    def test_serialize_list(self):
        serializer = DefaultBinarySerializer()

        result = serializer.serialize([], {})
        self.assertEqual(result, base64.b64encode('[]'.encode('utf-8')))

    def test_serializer_str(self):
        serializer = DefaultBinarySerializer()

        result = serializer.serialize('', {})
        self.assertEqual(result, base64.b64encode(''.encode('utf-8')))

    def test_serialize_tuple(self):
        serializer = DefaultBinarySerializer()

        result = serializer.serialize((), {})
        self.assertEqual(result, base64.b64encode('[]'.encode('utf-8')))
