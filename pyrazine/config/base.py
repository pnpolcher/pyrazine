from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Any, Dict, Iterable, Set


class BaseConfigurationReader(ABC):

    @property
    @abstractmethod
    def lazy_load(self) -> bool:
        raise NotImplementedError('Property not implemented in abstract base class.')

    @abstractmethod
    def read(self, key: str) -> str:
        raise NotImplementedError('Method not implemented in abstract base class.')

    @abstractmethod
    def read_many(self, keys: Iterable[str]) -> Dict[str, Any]:
        raise NotImplementedError('Method not implemented in abstract base class.')

    @abstractmethod
    def read_all(self) -> Dict[str, Any]:
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
    def register_reader(self, reader: BaseConfigurationReader):
        raise NotImplementedError('Method not implemented in abstract base class.')
