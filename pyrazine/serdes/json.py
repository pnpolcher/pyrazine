import json
import logging
from typing import Any, Dict

from pyrazine.serdes import BaseDeserializer

logger = logging.getLogger('JsonDeserializer')


class JsonDeserializer(BaseDeserializer):
    def __init__(self, json_ld: bool = False):
        self._json_ld = json_ld

    @classmethod
    def create(cls, parameters: Dict[str, Any]):
        variant = parameters.get('variant', None)
        json_ld = variant is not None and variant == 'ld'
        return JsonDeserializer(json_ld=json_ld)

    def deserialize(self, data: Any) -> Any:
        if not isinstance(data, str):
            error_msg = "JsonDeserializer needs a string as input to the deserialize method."
            logger.error(error_msg)
            raise ValueError(error_msg)

        return json.loads(data)
