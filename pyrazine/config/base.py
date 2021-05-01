from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Any, Dict, Set


class BaseConfigurationReader(ABC):

    @abstractmethod
    def read(self) -> Dict[str, str]:
        raise NotImplementedError('Method not implemented in abstract base class.')


class BaseConfigurationVault(ABC):

    @abstractmethod
    def get_decimal(self, key: str) -> Decimal:
        raise NotImplementedError('Method not implemented in abstract base class.')

    @abstractmethod
    def get_float(self, key: str) -> float:
        raise NotImplementedError('Method not implemented in abstract base class.')

    @abstractmethod
    def get_int(self, key: str) -> int:
        raise NotImplementedError('Method not implemented in abstract base class.')

    @abstractmethod
    def get_str(self, key: str) -> str:
        raise NotImplementedError('Method not implemented in abstract base class.')

    @abstractmethod
    def get_dict(self, key: str) -> Dict[str, Any]:
        raise NotImplementedError('Method not implemented in abstract base class.')

    @abstractmethod
    def get_set(self, key: str) -> Set[Any]:
        raise NotImplementedError('Method not implemented in abstract base class.')

    @abstractmethod
    def reader(self, reader):
        raise NotImplementedError('Method not implemented in abstract base class.')
