from decimal import Decimal
import logging
from typing import Any, List, Dict, Set

from pyrazine.config import BaseConfigurationReader, BaseConfigurationVault


logger = logging.getLogger('DefaultConfigurationVault')


class DefaultConfigurationVault(BaseConfigurationVault):
    """
    Simple implementation of a configuration vault.
    """

    _config_vault: Dict[str, Any]
    _readers: List[BaseConfigurationReader]

    def __init__(self):
        self._config_vault = {}
        self._readers = []
        logger.info('DefaultConfigurationVault initialized.')

    def _lazy_load_value(self, key: str) -> Any:

        result = None
        for reader in self._readers:
            result = reader.read(key)
            if result is not None:
                break

        return result

    def get_decimal(self, key: str) -> Decimal:
        value = self._config_vault.get(key, self._lazy_load_value(key))
        return Decimal(value) if value is not None else None

    def get_float(self, key: str) -> float:
        value = self._config_vault.get(key, self._lazy_load_value(key))
        return float(value) if value is not None else None

    def get_int(self, key: str) -> int:
        value = self._config_vault.get(key, self._lazy_load_value(key))
        return int(value) if value is not None else None

    def get_str(self, key: str) -> str:
        value = self._config_vault.get(key, self._lazy_load_value(key))
        return str(value) if value is not None else None

    def get_dict(self, key: str) -> Dict[str, Any]:
        pass

    def get_set(self, key: str) -> Set[Any]:
        pass

    def register_reader(self, reader: BaseConfigurationReader):
        if reader.lazy_load:
            self._readers.append(reader)
        else:
            for k, v in reader.read_all().items():
                self._config_vault[k] = v
