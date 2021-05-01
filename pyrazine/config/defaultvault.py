from decimal import Decimal
from typing import Any, List, Dict, Set

from pyrazine.config import BaseConfigurationReader, BaseConfigurationVault


class DefaultConfigurationVault(BaseConfigurationVault):

    _config_vault: Dict[str, Any]
    _reader_chain: List[BaseConfigurationReader]

    def __init__(self):
        self._config_vault = {}
        self._reader_chain = []

    def get_decimal(self, key: str) -> Decimal:
        value = self._config_vault.get(key, None)
        return Decimal(value) if value is not None else None

    def get_float(self, key: str) -> float:
        value = self._config_vault.get(key, None)
        return float(value) if value is not None else None

    def get_int(self, key: str) -> int:
        value = self._config_vault.get(key, None)
        return int(value) if value is not None else None

    def get_str(self, key: str) -> str:
        value = self._config_vault.get(key, None)
        return str(value) if value is not None else None

    def get_dict(self, key: str) -> Dict[str, Any]:
        pass

    def get_set(self, key: str) -> Set[Any]:
        pass

    def reader(self, reader: BaseConfigurationReader):
        self._reader_chain.append(reader)
        self._config_vault.update(reader.read())
