class LambdaCognitoIdentity(object):
    """
    Models the object passed as the identity field in the LambdaContext object
    passed to the function handler by AWS Lambda. To be used mainly in typing
    and testing.
    """

    def __init__(self,
                 cognito_identity_id: str,
                 cognito_identity_pool_id: str):

        self._cognito_identity_id = cognito_identity_id
        self._cognito_identity_pool_id = cognito_identity_pool_id

    @property
    def cognito_identity_id(self) -> str:
        return self._cognito_identity_id

    @property
    def cognito_identity_pool_id(self) -> str:
        return self._cognito_identity_pool_id
