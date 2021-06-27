import os

from pyrazine.config.base import BaseConfigurationMixin


class EnvironmentConfigurationMixin(BaseConfigurationMixin):
    """
    Implements a configuration mixin that takes prefixed environment variables
    (default prefix is APP), normalizes the key, and stores the data in a dictionary.
    """

    _ecmixin_prefix: str

    def __init__(self, prefix: str = 'app'):
        super(EnvironmentConfigurationMixin, self).__init__()
        self._registry.append(self)
        self._ecmixin_prefix = prefix.lower()

    def initialize(self):
        prefix_len = len(self._ecmixin_prefix) + 1
        return {
            var_name[prefix_len:].replace('_', '-').lower(): value
            for var_name, value in os.environ.items()
            if var_name.lower().startswith(f'{self._ecmixin_prefix}_')
        }
