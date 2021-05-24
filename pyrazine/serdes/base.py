from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseDeserializer(ABC):

    @classmethod
    @abstractmethod
    def create(cls, parameters: Dict[str, Any]):
        raise NotImplementedError('Method not implemented in abstract base class.')

    @abstractmethod
    def deserialize(self, data: Any, parameters: Optional[Dict[str, Any]] = None) -> Any:
        raise NotImplementedError('Method not implemented in abstract base class.')
