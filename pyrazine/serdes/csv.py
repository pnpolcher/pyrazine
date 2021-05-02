from typing import Any, Dict

from pyrazine.serdes import BaseDeserializer


class CsvDeserializer(BaseDeserializer):
    @classmethod
    def create(cls, parameters: Dict[str, Any]):
        pass

    def deserialize(self, data: Any) -> Any:
        pass
