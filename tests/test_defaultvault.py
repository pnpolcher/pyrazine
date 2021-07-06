from decimal import Decimal
import os
import unittest

from pyrazine.config import (
    DefaultConfigurationVault,
    EnvironmentConfigurationReader,
)


class TestDefaultConfigurationVault(unittest.TestCase):

    TEST_VAR_STR_VALUE = "1"
    TEST_VAR_INT_VALUE = int(TEST_VAR_STR_VALUE)

    def setUp(self) -> None:
        os.environ['APP_TESTVAR'] = self.TEST_VAR_STR_VALUE

    def tearDown(self) -> None:
        del os.environ['APP_TESTVAR']

    def test_env_get_str(self):
        vault = DefaultConfigurationVault()
        vault.register_reader(EnvironmentConfigurationReader())

        self.assertEqual(vault.get_str('testvar'), self.TEST_VAR_STR_VALUE)

    def test_env_get_int(self):
        vault = DefaultConfigurationVault()
        vault.register_reader(EnvironmentConfigurationReader())

        self.assertEqual(vault.get_int('testvar'), self.TEST_VAR_INT_VALUE)

    def test_env_get_decimal(self):
        vault = DefaultConfigurationVault()
        vault.register_reader(EnvironmentConfigurationReader())

        self.assertEqual(vault.get_decimal('testvar'), Decimal(self.TEST_VAR_INT_VALUE))
