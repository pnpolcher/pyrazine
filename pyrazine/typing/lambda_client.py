class LambdaClient(object):
    """
    Models the client_context object in the LambdaContext object passed to the
    function handler by AWS Lambda. To be used mainly for typing and testing
    purposes.
    """

    def __init__(self,
                 installation_id: str,
                 app_title: str,
                 app_version_name: str,
                 app_version_code: str,
                 app_package_name: str):
        """
        Initializes an instance of the LambdaClient class with mock data.

        :param installation_id: Installation ID of the mobile application.
        :param app_title: App title.
        :param app_version_name: Version name.
        :param app_version_code: Version code.
        :param app_package_name: Package name.
        """

        self._installation_id = installation_id
        self._app_title = app_title
        self._app_version_name = app_version_name
        self._app_version_code = app_version_code
        self._app_package_name = app_package_name

    @property
    def installation_id(self) -> str:
        return self._installation_id

    @property
    def app_title(self) -> str:
        return self._app_title

    @property
    def app_version_name(self) -> str:
        return self._app_version_name

    @property
    def app_version_code(self) -> str:
        return self._app_version_code

    @property
    def app_package_name(self) -> str:
        return self._app_package_name
