from typing import Dict

from pyrazine.typing.lambda_client import LambdaClient


class LambdaClientContext(object):
    """
    Models the client_context property of the context object passed to function
    handlers by AWS Lambda. Class mainly for typing and testing uses.
    """

    def __init__(self,
                 client: LambdaClient,
                 custom: Dict[str, object],
                 env: Dict[str, object]):

        self._client = client
        self._custom = custom
        self._env = env

    @property
    def client(self) -> LambdaClient:
        return self._client

    @property
    def custom(self) -> Dict[str, object]:
        return self._custom

    @property
    def env(self) -> Dict[str, object]:
        return self._env
