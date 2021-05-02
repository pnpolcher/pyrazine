from typing import Dict, Any

from pyrazine.serdes import BaseDeserializer


class DefaultBinaryDeserializer(BaseDeserializer):
    @classmethod
    def create(cls, parameters: Dict[str, Any]):
        pass

    def deserialize(self, data: Any):
        pass


class CompressedBinaryDeserializer(BaseDeserializer):
    @classmethod
    def create(cls, parameters: Dict[str, Any]):
        pass

    def deserialize(self, data: Any):
        pass
