from base64 import b64decode
import logging
from typing import Any, Dict, Optional

from pyrazine.serdes import BaseDeserializer

logger = logging.getLogger('DummyDeserializer')


class DummyDeserializer(BaseDeserializer):
    def __init__(self, is_base64_encoded: bool):
        self._is_base64_encoded = is_base64_encoded

    @classmethod
    def create(cls, parameters: Dict[str, Any]):
        is_base64_encoded = parameters.get('is_base64_encoded', None)
        if is_base64_encoded is None:
            raise ValueError('DummyDeserializer expects an is_base64_encoded boolean parameter.')
        return DummyDeserializer(is_base64_encoded=is_base64_encoded)

    def deserialize(self, data: Any, parameters: Optional[Dict[str, Any]] = None) -> Any:
        if data is None:
            return ''

        if not isinstance(data, str):
            error_msg = 'DummyDeserializer expects a string parameter as data.'
            logger.error(error_msg)
            raise ValueError(error_msg)

        return b64decode(data) if self._is_base64_encoded else data
