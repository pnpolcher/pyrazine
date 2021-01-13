import time

from pyrazine.typing.lambda_client_context import LambdaClientContext
from pyrazine.typing.lambda_cognito_identity import LambdaCognitoIdentity


class LambdaContext(object):
    """
    Models the context object passed to the function handler by AWS Lambda. To
    be used mainly for typing and testing purposes.
    """

    # The maximum execution time allowed for AWS Lambda functions (15 minutes)
    # in milliseconds.
    MAX_EXEC_TIME_IN_MILLIS = 15 * 60 * 1000

    def __init__(self,
                 function_name: str,
                 function_version: str,
                 invoked_function_arn: str,
                 memory_limit_in_mb: int,
                 aws_request_id: str,
                 log_group_name: str,
                 log_stream_name: str,
                 identity: LambdaCognitoIdentity,
                 client_context: LambdaClientContext):
        """
        Initializes an instance of the LambdaContext class.

        :param function_name: The name of the Lambda function.
        :param function_version: The version of the Lambda function.
        :param invoked_function_arn: The ARN that is used to invoke the function.
        :param memory_limit_in_mb: The amount of memory allocated for the Lambda
        function, in megabytes.
        :param aws_request_id: The identifier of the invocation request.
        :param log_group_name: The log group of the Lambda function.
        :param log_stream_name: The log stream for the function instance.
        :param identity: Information about the Amazon Cognito identity that
        authorized the request. (Only for mobile apps)
        :param client_context: Returns the number of milliseconds left before
        the execution times out. (Only for mobile apps)
        """

        self._function_name = function_name
        self._function_version = function_version
        self._invoked_function_arn = invoked_function_arn
        self._memory_limit_in_mb = memory_limit_in_mb
        self._aws_request_id = aws_request_id
        self._log_group_name = log_group_name
        self._log_stream_name = log_stream_name
        self._identity = identity
        self._client_context = client_context

        self._start_time = time.time()

    @property
    def function_name(self) -> str:
        """
        The name of the Lambda function.
        """
        return self._function_name

    @property
    def function_version(self) -> str:
        """
        The version of the Lambda function.
        """
        return self._function_version

    @property
    def invoked_function_arn(self) -> str:
        """
        The ARN that is used to invoke the function.
        """
        return self._invoked_function_arn

    @property
    def memory_limit_in_mb(self) -> int:
        """
        The amount of memory allocated for the Lambda function, in megabytes.
        """
        return self._memory_limit_in_mb

    @property
    def aws_request_id(self) -> str:
        """
        The identifier of the invocation request.
        """
        return self._aws_request_id

    @property
    def log_group_name(self) -> str:
        """
        The log group of the Lambda function.
        """
        return self._log_group_name

    @property
    def log_stream_name(self) -> str:
        """
        The log stream for the function instance.
        """
        return self._log_stream_name

    @property
    def identity(self) -> LambdaCognitoIdentity:
        """
        Information about the Amazon Cognito identity that authorized the request.
        (Only for mobile apps)
        """
        return self._identity

    @property
    def client_context(self) -> LambdaClientContext:
        """
        Client context that has been provided to Lambda by the client application.
        (Only for mobile apps)
        """
        return self._client_context

    def get_remaining_time_in_millis(self) -> int:
        """
        Returns the number of milliseconds left before the execution times out.
        (Mocked)
        """
        time_elapsed = time.time() - self._start_time
        return int((self.MAX_EXEC_TIME_IN_MILLIS - time_elapsed) * 1000)
