import logging

from typing import Dict

from pyrazine.auth import CognitoAuthorizer, DDBAuthStorage, SimpleUserProfile
from pyrazine.handlers import ApiGatewayEventHandler
from pyrazine.jwt import JwtToken
from pyrazine.response import HttpResponse


logger = logging.getLogger('test')
logger.setLevel(logging.DEBUG)
handler = ApiGatewayEventHandler(
    authorizer=CognitoAuthorizer(
        user_pool_id='',
        client_id='',
        region='',
        auth_storage=DDBAuthStorage(
            user_table_name='',
            user_profile_cls=SimpleUserProfile)
    )
)


@handler.authorizer.auth(roles=['admin'])
@handler.route(path='/auth', methods=('GET',), trace=True)
def auth_root_get_handler(
        token: JwtToken,
        body: Dict[str, object],
        context: Dict[str, object]) -> HttpResponse:

    return HttpResponse(200, body={'hello': 'world'})


@handler.route(path='/noauth', methods=('GET',), trace=True)
def noauth_root_get_handler(
        token: JwtToken,
        body: Dict[str, object],
        context: Dict[str, object]) -> HttpResponse:

    return HttpResponse(200, body={'hello': 'world'})


def lambda_handler(event, context):
    response = handler.handle_request(event, context)
    return response
