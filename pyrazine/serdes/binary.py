from base64 import b64decode
import logging
from typing import Dict, Any, Optional

from pyrazine.serdes import BaseDeserializer

logger = logging.getLogger('BinaryDeserializer')


class DefaultBinaryDeserializer(BaseDeserializer):
    def __init__(self, mime_type: str):
        self._mime_type = mime_type

    @property
    def mime_type(self) -> str:
        return self._mime_type

    @classmethod
    def create(cls, parameters: Dict[str, Any]):
        mime_type = parameters.get('mime_type', 'application/octet-stream')
        return DefaultBinaryDeserializer(mime_type=mime_type)

    def deserialize(self, data: Any, parameters: Optional[Dict[str, Any]] = None) -> Any:
        if not isinstance(data, str):
            error_message = "DefaultBinaryDeserializer expects a Base64 encoded binary payload " +\
                            "as argument for the deserialize method"
            logger.error(error_message)
            raise ValueError(error_message)

        return b64decode(data)


class CompressedBinaryDeserializer(BaseDeserializer):
    @classmethod
    def create(cls, parameters: Dict[str, Any]):
        pass

    def deserialize(self, data: Any, parameters: Optional[Dict[str, Any]] = None) -> Any:
        pass
