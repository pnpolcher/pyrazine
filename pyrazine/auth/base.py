from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Any, Dict, Iterable, List, Set, Tuple, Union

from pyrazine.jwt import JwtToken


class BaseAuthorizer(ABC):
    
    @abstractmethod
    def authorizer(self,
                   roles: Union[List[str], Tuple[str]],
                   token: JwtToken,
                   fetch_full_profile: bool = False) -> Any:

        raise NotImplementedError('Method not implemented in abstract base class.')


class BaseUserProfile(ABC):

    _roles: Set[str]

    @property
    @abstractmethod
    def roles(self) -> Set[str]:
        raise NotImplementedError('Method not implemented in abstract base class.')

    @roles.setter
    @abstractmethod
    def roles(self, value: str) -> None:
        raise NotImplementedError('Method not implemented in abstract base class.')

    @classmethod
    @abstractmethod
    def from_document(cls, doc: Dict[str, Union[str, int, float, Decimal, Iterable, object]]):
        raise NotImplementedError('Method not implemented in abstract base class.')

    @abstractmethod
    def to_document(self) -> Dict[str, Union[str, int, float, Decimal, Iterable, object]]:
        raise NotImplementedError('Method not implemented in abstract base class.')


class BaseAuthStorage(ABC):

    @abstractmethod
    def get_user_profile(self, user_id: str) -> BaseUserProfile:
        raise NotImplementedError('Method not implemented in abstract base class.')

    @abstractmethod
    def get_user_roles(self, user_id: str) -> Set[str]:
        raise NotImplementedError('Method not implemented in abstract base class.')

    @abstractmethod
    def put_user_profile(self, user_id: str, user_profile: BaseUserProfile) -> None:
        raise NotImplementedError('Method not implemented in abstract base class.')
