import os
from typing import Any, Dict

from pyrazine.config.base import BaseConfigurationReader


class EnvironmentConfigurationReader(BaseConfigurationReader):
    """
    Implements a configuration mixin that takes prefixed environment variables
    (default prefix is APP), normalizes the key, and stores the data in a dictionary.
    """

    _ecmixin_prefix: str

    def __init__(self, prefix: str = 'app'):
        super(EnvironmentConfigurationReader, self).__init__()
        self._ecmixin_prefix = prefix.lower()

    @property
    def lazy_load(self) -> bool:
        return False

    def read(self, key: str) -> str:
        pass

    def read_all(self) -> Dict[str, Any]:
        prefix_len = len(self._ecmixin_prefix) + 1

        return {
            var_name[prefix_len:].replace('_', '-').lower(): value
            for var_name, value in os.environ.items()
            if var_name.lower().startswith(f'{self._ecmixin_prefix}_')
        }
