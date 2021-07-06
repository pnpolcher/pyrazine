import logging
from typing import Any, Dict, Optional

import boto3
from botocore.exceptions import ClientError

from pyrazine.config.base import BaseConfigurationReader


logger = logging.getLogger('SSMConfigurationReader')


class SSMConfigurationReader(BaseConfigurationReader):

    _app_prefix: str
    _decrypt_parameters: bool
    _lazy_load: bool

    def __init__(self,
                 region_name: Optional[str] = None,
                 lazy_load: bool = True,
                 app_prefix: Optional[str] = None,
                 decrypt_parameters: bool = False):

        self._ssm_client = boto3.client('ssm', region_name=region_name)
        self._app_prefix = app_prefix
        self._lazy_load = lazy_load
        self._decrypt_parameters = decrypt_parameters

    @property
    def lazy_load(self) -> bool:
        return self._lazy_load

    def read(self, key: str) -> str:

        try:
            response = self._ssm_client.get_parameter(
                Name=key,
                WithDecryption=self._decrypt_parameters,
            )
        except ClientError as e:
            logger.exception(e)
            raise

        return response['Parameter']['Value']

    def read_all(self) -> Dict[str, Any]:
        if self._app_prefix is None:
            raise RuntimeError('Application prefix must be set to read all parameters.')

        raise NotImplementedError('TODO: Implement')
