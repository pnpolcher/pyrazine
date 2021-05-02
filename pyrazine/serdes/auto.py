import logging
from typing import Any, ClassVar, Dict

from pyrazine.events import HttpEvent
from pyrazine.serdes import (
    BaseDeserializer,
    CompressedBinaryDeserializer,
    CsvDeserializer,
    DefaultBinaryDeserializer,
    DummyDeserializer,
    JsonDeserializer,
    XmlDeserializer,
)

logger = logging.getLogger('AutoDeserialization')


class HttpRequestAutoDeserializer(BaseDeserializer):
    """
    Implements a request deserializer that automatically infers the appropriate deserialization
    method based on the MIME type specified in the content-type HTTP header.
    """
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
            'parameters': {
                'mime_type': 'application/octet-stream'
            },
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
        'image/gif': {
            'deserializer': DefaultBinaryDeserializer,
            'parameters': {
                'mime_type': 'image/gif',
            },
        },
        'image/jpeg': {
            'deserializer': DefaultBinaryDeserializer,
            'parameters': {
                'mime_type': 'image/jpeg',
            },
        },
        'image/png': {
            'deserializer': DefaultBinaryDeserializer,
            'parameters': {
                'mime_type': 'image/png',
            },
        },
        'image/tiff': {
            'deserializer': DefaultBinaryDeserializer,
            'parameters': {
                'mime_type': 'image/tiff',
            },
        },
        'text/csv': CsvDeserializer,
        'text/plain': {
            'deserializer': None,
            'parameters': {}
        },
    }

    _deserializer_instance: BaseDeserializer

    def __init__(self, event: HttpEvent):
        self._create_deserializer(event)

    def _create_deserializer(self, event: HttpEvent):
        content_type = event.headers.get('content-type', None)
        if content_type is not None:
            self._deserializer_instance = self._create_from_mime_type(content_type, event)
        else:
            self._deserializer_instance = self._get_default_deserializer(event)

    @staticmethod
    def _get_default_deserializer(event: HttpEvent) -> BaseDeserializer:
        """
        Creates a default deserializer when the data format cannot be inferred from the
        MIME type.
        :param event: The Lambda HTTP event.
        :return: An instance of the default deserializer.
        """
        # Cannot infer the type of the data sent, so we'll simply discriminate between
        # base64-encoded and plain text data.
        return DummyDeserializer.create({
            'is_base64_encoded': event.is_base64_encoded
        })

    def _create_from_mime_type(self, mime_type: str, event: HttpEvent) -> BaseDeserializer:
        """
        Creates a new deserializer whose type is inferred from the content-type HTTP header.

        :param mime_type: The MIME type passed to the function as the content-type header.
        :param event: The Lambda HTTP event object.
        :return: An instance of the deserializer object that best matches the mime type specified.
        """

        deserializer_entry = self.MIME_TYPE_TABLE[mime_type.strip()]
        deserializer_class = deserializer_entry.get('deserializer', None)
        if deserializer_class is None:
            logger.warning(f'Deserializer dictionary has no deserializer class for MIME type ' +
                           '{mime_type}! Falling back to default.')
            return self._get_default_deserializer(event)
        return deserializer_class.create(deserializer_entry.get('parameters', {}))

    @property
    def deserializer(self) -> BaseDeserializer:
        return self._deserializer_instance

    @classmethod
    def create(cls, parameters: Dict[str, Any]):
        event = parameters.get('event', None)
        if event is None:
            raise ValueError('Missing event parameter for auto deserializer.')
        return HttpRequestAutoDeserializer(event)

    def deserialize(self, data: Any):
        return self._deserializer_instance.deserialize(data)
