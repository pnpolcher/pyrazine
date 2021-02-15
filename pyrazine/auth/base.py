from abc import ABC
from typing import Set


class BaseAuthorizer(ABC):
    pass


class BaseUserProfile(ABC):

    _roles: Set[str]

    @property
    def roles(self):
        return self._roles


class BaseAuthStorage(ABC):

    def get_user_profile(self, user_id: str) -> BaseUserProfile:
        pass

    def get_user_roles(self, user_id: str) -> Set[str]:
        pass

