import logging

from pyrazine.auth import CognitoAuthorizer, DDBAuthStorage, SimpleUserProfile
from pyrazine.handlers import ApiGatewayEventHandler
from pyrazine.requests.httprequest import HttpRequest
from pyrazine.response import HttpResponse


logger = logging.getLogger('test')
logger.setLevel(logging.DEBUG)
handler = ApiGatewayEventHandler(
    authorizer=CognitoAuthorizer(
        user_pool_id='',
        client_ids=(),
        region='',
        auth_storage=DDBAuthStorage(
            user_table_name='',
            user_profile_cls=SimpleUserProfile)
    )
)


@handler.authorizer.auth(roles=['admin'])
@handler.route(path='/auth', methods=('GET',), trace=True)
def auth_root_get_handler(request: HttpRequest) -> HttpResponse:

    return HttpResponse(200, body={'hello': 'world'})


@handler.route(path='/noauth', methods=('GET',), trace=True)
def noauth_root_get_handler(request: HttpRequest) -> HttpResponse:

    return HttpResponse(200, body={'hello': 'world'})


def lambda_handler(event, context):
    response = handler.handle_request(event, context)
    return response
