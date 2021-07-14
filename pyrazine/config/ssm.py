import logging
from typing import Any, Dict, Iterable, Optional

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

    def _ssm_to_dict(self, response: Any) -> Dict[str, Any]:
        result: Dict[str, Any] = {}

        for parameter in response['Parameters']:
            param_name = str(parameter['Name'])
            if parameter['Type'] == 'StringList':
                value = str(parameter['Value'])
                result[param_name] = value.split(',')
            else:
                result[param_name] = parameter['Value']

        return result

    def read(self, key: str) -> str:

        try:
            response = self._ssm_client.get_parameter(
                Name=key,
                WithDecryption=self._decrypt_parameters,
            )
        except ClientError as e:
            logger.exception(e)
            raise

        parameter = response['Parameter']

        return str(parameter['Value']).split(',')\
            if parameter['Type'] == 'StringList' else parameter['Value']

    def read_many(self, keys: Iterable[str]) -> Dict[str, Any]:

        try:
            response = self._ssm_client.get_parameters(
                Names=list(keys),
                WithDecryption=self._decrypt_parameters,
            )

            return self._ssm_to_dict(response)

        except ClientError as e:
            logger.exception(e)
            raise

    def read_all(self) -> Dict[str, Any]:
        if self._app_prefix is None:
            raise RuntimeError('Application prefix must be set to read all parameters.')

        try:
            response = self._ssm_client.get_parameters_by_path(
                Path=self._app_prefix,
                Recursive=True,
                WithDecryption=self._decrypt_parameters,
            )

            return self._ssm_to_dict(response)

        except ClientError as e:
            logger.exception(e)
            raise
