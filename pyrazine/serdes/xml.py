from typing import Any, Dict, Optional

from pyrazine.serdes import BaseDeserializer


class XmlDeserializer(BaseDeserializer):
    @classmethod
    def create(cls, parameters: Dict[str, Any]):
        pass

    def deserialize(self, data: Any, parameters: Optional[Dict[str, Any]] = None) -> Any:
        pass
