from base64 import b64decode, b64encode
from decimal import Decimal
import logging
import struct
import sys
from typing import Dict, Any, Optional

from pyrazine.serdes import BaseDeserializer, BaseSerializer

logger = logging.getLogger('BinaryDeserializer')


class DefaultBinaryDeserializer(BaseDeserializer):
    def __init__(self, mime_type: str):
        self._mime_type = mime_type

    @property
    def mime_type(self) -> str:
        return self._mime_type

    @classmethod
    def create(cls, parameters: Dict[str, Any]):
        mime_type = parameters.get('mime_type', 'application/octet-stream')
        return DefaultBinaryDeserializer(mime_type=mime_type)

    def deserialize(self, data: Any, parameters: Optional[Dict[str, Any]] = None) -> Any:
        if not isinstance(data, str):
            error_message = "DefaultBinaryDeserializer expects a Base64 encoded binary payload " +\
                            "as argument for the deserialize method"
            logger.error(error_message)
            raise ValueError(error_message)

        return b64decode(data)


class DefaultBinarySerializer(BaseSerializer):

    _int_length: int
    _byteorder: str
    _int_signed: bool
    _mime_type: str

    def __init__(self,
                 int_length: int = sys.int_info.sizeof_digit,
                 byteorder: str = sys.byteorder,
                 int_signed: bool = False,
                 mime_type: str = 'application/octet-stream'):
        """
        Initializes a new instance of the DefaultBinarySerializer class.

        :param int_length: Defaults to sys.int_info.sizeof_digit. The number of bytes to use to represent an integer
                           value as bytes.
        :param byteorder: Defaults to "little". Valid values are "little" and "big".
            big    - The most significant byte is at the beginning of the byte array.
            little - The most significant byte is at the end of the byte array.
        :param int_signed: Defaults to False. Whether the integer passed is signed. If a negative integer is passed
                           while int_signed is set to False, the call will fail.
        :param mime_type Defaults to "application/octet-stream". The MIME type to return to the code building the
                         HTTP response.
        """

        self._int_length = int_length
        self._byteorder = byteorder
        self._int_signed = int_signed
        self._mime_type = mime_type

    @property
    def is_base64_encoded(self) -> bool:
        return True

    @property
    def mime_type(self) -> str:
        return self._mime_type

    @classmethod
    def create(cls, parameters: Dict[str, Any]):
        """
        Creates a new instance of the DefaultBinarySerializer class.

        The following parameters can be optionally passed to the serializer class:
            byteorder:  Defaults to "little". Valid values are "little" and "big".
                big    - The most significant byte is at the beginning of the byte array.
                little - The most significant byte is at the end of the byte array.
            int_length: Defaults to sys.int_info.sizeof_digit. The number of bytes to use to represent an integer value
                        as bytes.
            int_signed: Defaults to False. Whether the integer passed is signed. If a negative integer is passed while
                        int_signed is set to False, the call will fail.
            mime_type:  Defaults to "application/octet-stream". The MIME type to return to the code building the
                        HTTP response.

        :param parameters: Optional parameters to configure the serializer.
        :return: A new instance of the DefaultBinarySerializer class.
        """

        int_length = parameters.get('int_length', sys.int_info.sizeof_digit)
        byteorder = parameters.get('byteorder', sys.byteorder)
        int_signed = parameters.get('int_signed', False)
        mime_type = parameters.get('mime_type', 'application/octet-stream')

        serializer = cls(int_length=int_length, byteorder=byteorder, int_signed=int_signed, mime_type=mime_type)
        return serializer

    def serialize(self, data: Any, parameters: Optional[Dict[str, Any]] = None) -> Any:
        if isinstance(data, dict) or isinstance(data, list) or isinstance(data, tuple):
            import json
            from pyrazine.serdes.json import DefaultJSONEncoder
            payload = json.dumps(data, cls=DefaultJSONEncoder).encode('utf-8')
        elif isinstance(data, str):
            payload = data.encode('utf-8')
        elif isinstance(data, int):
            payload = data.to_bytes(self._int_length, self._byteorder, signed=self._int_signed)
        elif isinstance(data, float):
            payload = bytes(struct.pack("f", data))
        elif isinstance(data, Decimal):
            payload = str(data).encode('utf-8')
        elif isinstance(data, bytes):
            payload = data
        else:
            error_message = "Data type not supported by DefaultBinarySerializer."
            logger.error(error_message)
            raise ValueError(error_message)

        return b64encode(payload)


class CompressedBinaryDeserializer(BaseDeserializer):
    @classmethod
    def create(cls, parameters: Dict[str, Any]):
        pass

    def deserialize(self, data: Any, parameters: Optional[Dict[str, Any]] = None) -> Any:
        pass
