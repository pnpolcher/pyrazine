from typing import Dict, Iterable, Optional, Set

from pyrazine.auth.base import BaseUserProfile


class SimpleUserProfile(BaseUserProfile):

    _email: str = None
    _family_name: str = None
    _given_name: str = None
    _roles: Set[str] = None
    _user_id: str = None

    def __init__(self,
                 email: str,
                 family_name: str,
                 given_name: str,
                 roles: Set[str],
                 user_id: str):

        self._email = email
        self._family_name = family_name
        self._given_name = given_name
        self._roles = roles
        self._user_id = user_id

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, value: str) -> None:
        self._email = value

    @property
    def given_name(self) -> str:
        return self._given_name

    @given_name.setter
    def given_name(self, value: str) -> None:
        self._given_name = value

    @property
    def family_name(self) -> str:
        return self._family_name

    @family_name.setter
    def family_name(self, value: str) -> None:
        self._family_name = value

    @property
    def roles(self) -> Set[str]:
        return self._roles

    @roles.setter
    def roles(self, value: Set[str]) -> None:
        self._roles = value

    @classmethod
    def from_document(cls, doc: Dict[str, Optional[Iterable, object]]):
        return cls(
            email=doc['email'] if 'email' in doc else None,
            family_name=doc['familyName'] if 'familyName' in doc else None,
            given_name=doc['givenName'] if 'givenName' in doc else None,
            roles=set(doc['roles']) if 'roles' in doc else None,
            user_id=doc['userId'] if 'userId' in doc else None,
        )

    def to_document(self) -> Dict[str, Optional[Iterable, object]]:
        return {
            'email': self._email,
            'familyName': self._family_name,
            'givenName': self._given_name,
            'roles': list(self._roles),
            'user_id': self._user_id
        }
