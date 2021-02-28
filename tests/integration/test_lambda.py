import logging

from typing import Dict

from pyrazine.handlers import LambdaHandler
from pyrazine.jwt import JwtToken
from pyrazine.response import HttpResponse


logger = logging.getLogger('test')
logger.setLevel(logging.DEBUG)
handler = LambdaHandler()


@handler.route(path='/', methods=('GET',), trace=True)
def root_handler(token: JwtToken, body: Dict[str, object]) -> HttpResponse:
    return HttpResponse(200, body={'hello': 'world'})


def lambda_handler(event, context):
    response = handler.handle_request(event, context)
    return response
