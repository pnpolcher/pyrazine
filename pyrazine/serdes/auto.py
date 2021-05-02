from base64 import b64decode
import logging
from typing import Callable, ClassVar

from pyrazine.events import HttpEvent
from pyrazine.serdes import (
    BaseDeserializer,
    CompressedBinaryDeserializer,
    CsvDeserializer,
    DefaultBinaryDeserializer,
    JsonDeserializer,
    XmlDeserializer,
)

logger = logging.getLogger('AutoDeserialization')


class HttpRequestAutoDeserializer(object):
    MIME_TYPE_TABLE: ClassVar = {
        'application/json': {
            'deserializer': JsonDeserializer,
            'parameters': {},
        },
        'application/ld+json': {
            'deserializer': JsonDeserializer,
            'parameters': {
                'variant': 'ld',
            },
        },
        'application/gzip': {
            'deserializer': CompressedBinaryDeserializer,
            'parameters': {
                'variant': 'gzip',
            },
        },
        'application/octet-stream': {
            'deserializer': DefaultBinaryDeserializer,
            'parameters': {},
        },
        'application/xml': {
            'deserializer': XmlDeserializer,
            'parameters': {},
        },
        'application/zip': {
            'deserializer': CompressedBinaryDeserializer,
            'parameters': {
                'variant': 'zip',
            },
        },
        'image/gif': '',
        'image/jpeg': '',
        'image/png': '',
        'image/tiff': '',
        'text/csv': CsvDeserializer,
        'text/plain': '',
    }

    _deserializer_instance: BaseDeserializer

    def __init__(self, event: HttpEvent):
        self._create_deserializer(event)

    def _create_deserializer(self, event: HttpEvent):
        content_type = event.headers.get('content-type', None)
        if content_type is not None:
            self._deserialize_fn = self._create_from_mime_type(content_type, event)
        else:
            self._deserialize_fn = self._get_default_deserialize_fn(event)

    @staticmethod
    def _get_default_deserialize_fn(event: HttpEvent) -> Callable:
        # Cannot infer the type of the data sent, so we'll simply discriminate between
        # base64-encoded and plain text data.
        if event.is_base64_encoded:
            return lambda x: b64decode(x)
        else:
            return lambda x: x

    def _create_from_mime_type(self, mime_type: str, event: HttpEvent) -> Callable:
        deserializer_entry = self.MIME_TYPE_TABLE[mime_type.strip()]
        deserializer_class = deserializer_entry.get('deserializer', None)
        if deserializer_class is None:
            logger.warning(f'Deserializer dictionary has no deserializer class for MIME type ' +
                           '{mime_type}! Falling back to default.')
            return self._get_default_deserialize_fn(event)
        self._deserializer_instance = \
            deserializer_class.create(deserializer_entry.get('parameters', {}))
        return self._deserializer_instance.deserialize

    @property
    def deserializer(self) -> BaseDeserializer:
        return self._deserializer_instance
