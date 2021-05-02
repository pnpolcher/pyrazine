from typing import Dict, Any

from pyrazine.serdes import BaseDeserializer


class XmlDeserializer(BaseDeserializer):
    @classmethod
    def create(cls, parameters: Dict[str, Any]):
        pass

    def deserialize(self, data: Any):
        pass
