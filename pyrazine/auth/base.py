from abc import ABC, abstractmethod
from typing import Dict, Iterable, List, Optional, Set, Tuple

from pyrazine.handlers import HandlerCallable


class BaseAuthorizer(ABC):
    
    @abstractmethod
    def auth(self,
             handler: HandlerCallable,
             roles: Optional[List[str], Tuple[str]],
             fetch_full_profile: bool = False) -> HandlerCallable:

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
    def from_document(cls, doc: Dict[str, Optional[Iterable, object]]):
        raise NotImplementedError('Method not implemented in abstract base class.')

    @abstractmethod
    def to_document(self) -> Dict[str, Optional[Iterable, object]]:
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
