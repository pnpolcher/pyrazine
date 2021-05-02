from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseDeserializer(ABC):

    @classmethod
    @abstractmethod
    def create(cls, parameters: Dict[str, Any]):
        raise NotImplementedError('Method not implemented in abstract base class.')

    @abstractmethod
    def deserialize(self, data: Any):
        raise NotImplementedError('Method not implemented in abstract base class.')
