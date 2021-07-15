from decimal import Decimal
import json
import logging
from typing import Any, Dict, Optional

from pyrazine.serdes import BaseDeserializer, BaseSerializer

logger = logging.getLogger('JsonDeserializer')


class DefaultJSONEncoder(json.JSONEncoder):
    """
    Class that implements serialization for types other than those supported
    by JSONEncoder, and that may come up in JSON in Lambda functions.
    """
    def default(self, o):
        if isinstance(o, Decimal):
            return str(o)
        elif isinstance(o, set):
            return list(o)
        else:
            return super().default(o)


class JsonDeserializer(BaseDeserializer):
    def __init__(self, json_ld: bool = False):
        self._json_ld = json_ld

    @classmethod
    def create(cls, parameters: Dict[str, Any]):
        variant = parameters.get('variant', None)
        json_ld = variant is not None and variant == 'ld'
        return cls(json_ld=json_ld)

    def deserialize(self, data: Any, parameters: Optional[Dict[str, Any]] = None) -> Any:
        if data is None:
            return {}

        if not isinstance(data, str):
            error_msg = "JsonDeserializer needs a string as input to the deserialize method."
            logger.error(error_msg)
            raise ValueError(error_msg)

        return json.loads(data)


class JsonSerializer(BaseSerializer):

    def __init__(self, encoder_class: Optional[json.JSONEncoder] = None, json_ld: bool = False):
        self._json_ld = json_ld
        self._encoder_class = encoder_class or DefaultJSONEncoder

    @property
    def is_base64_encoded(self) -> bool:
        return False

    @property
    def mime_type(self) -> str:
        return "application/json"

    @classmethod
    def create(cls, parameters: Dict[str, Any]):

        encoder_class = parameters.get('encoder_class')
        variant = parameters.get('variant', None)
        json_ld = variant is not None and variant == 'ld'
        return cls(json_ld=json_ld, encoder_class=encoder_class)

    def serialize(self, data: Any, parameters: Optional[Dict[str, Any]] = None) -> Any:
        if data is None:
            return ""

        return json.dumps(
            data,
            cls=self._encoder_class
        )
