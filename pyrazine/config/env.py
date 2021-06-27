import os
from typing import Dict

from pyrazine.config import BaseConfigurationReader


class EnvironmentConfigurationReader(BaseConfigurationReader):
    """
    Implements a configuration reader that takes prefixed environment variables
    (default prefix is APP), normalizes the key, and stores the data in a dictionary.
    """

    _prefix: str

    def __init__(self, prefix: str = 'app'):
        self._prefix = prefix.lower()

    def read(self) -> Dict[str, str]:
        prefix_len = len(self._prefix) + 1
        return {
            var_name[prefix_len:].replace('_', '-').lower(): value
            for var_name, value in os.environ.items()
            if var_name.lower().startswith(f'{self._prefix}_')
        }
