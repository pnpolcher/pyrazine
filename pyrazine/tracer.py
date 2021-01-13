from typing import Any, Dict, Callable

import aws_xray_sdk
import aws_xray_sdk.core
from aws_xray_sdk.core.models import subsegment as xray_subsegment


class Tracer(object):
    """
    Wrapper class for X-Ray tracing features.
    """

    def __init__(self,
                 recorder: aws_xray_sdk.core.xray_recorder = None,
                 service_name: str = 'unknown_service'):

        self._recorder = recorder if recorder is not None \
            else aws_xray_sdk.core.xray_recorder
        self._service_name = service_name

    @property
    def recorder(self):
        return self._recorder

    def trace_exception(self,
                        handler_name: str = None,
                        exception: Exception = None,
                        subsegment: xray_subsegment = None):

        if exception is None or subsegment is None:
            return

        subsegment.put_metadata(
            key=f'{handler_name}__exception',
            value=exception,
            namespace=self._service_name
        )

    def trace_route(self,
                    handler_name: str = None,
                    persist_response: bool = False,
                    response_data: Any = None,
                    subsegment: xray_subsegment = None):

        if not persist_response or response_data is None or subsegment is None:
            return

        subsegment.put_metadata(
            key=f'{handler_name}__response',
            value=response_data,
            namespace=self._service_name
        )

    def in_subsegment(self, name: str = None, **kwargs):
        return self._recorder.in_subsegment(name=name, **kwargs)

    @staticmethod
    def _disable_tracing():
        aws_xray_sdk.global_sdk_config.set_sdk_enabled(False)
