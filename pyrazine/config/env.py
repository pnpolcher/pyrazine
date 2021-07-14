import logging
import os
from typing import Any, Dict, Iterable

from pyrazine.config.base import BaseConfigurationReader


logger = logging.getLogger('EnvironmentConfigurationReader')


class EnvironmentConfigurationReader(BaseConfigurationReader):
    """
    Implements a configuration mixin that takes prefixed environment variables
    (default prefix is APP), normalizes the key, and stores the data in a dictionary.
    """

    _ec_prefix: str
    _prefix_len: int

    def __init__(self, prefix: str = 'app'):
        super(EnvironmentConfigurationReader, self).__init__()
        self._ec_prefix = prefix.lower()
        self._prefix_len = len(self._ec_prefix) + 1

    def _get_variable_name(self, var_name: str) -> str:
        return var_name[self._prefix_len:].replace('_', '-').lower()

    def _get_env_variable_name(self, var_name: str) -> str:
        return f"{self._ec_prefix}_{var_name.replace('_', '-')}".upper()

    @property
    def lazy_load(self) -> bool:
        return False

    def read(self, key: str) -> str:
        try:
            return os.environ[self._get_env_variable_name(key)]
        except KeyError as e:
            logger.exception(e)
            raise

    def read_many(self, keys: Iterable[str]) -> Dict[str, Any]:

        result: Dict[str, Any] = {}

        for key in keys:
            value = os.environ.get(self._get_env_variable_name(key))
            if value is not None:
                result[key] = value

        return result

    def read_all(self) -> Dict[str, Any]:
        return {
            self._get_variable_name(env_var_name): value
            for env_var_name, value in os.environ.items()
            if env_var_name.lower().startswith(f'{self._ec_prefix}_')
        }
