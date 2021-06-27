# Writing a Hello World service using Pyrazine and AWS Lambda

## Introduction

To understand the basics of Pyrazine, we will write a «Hello, World!» service that will
introduce you to the necessary building blocks to build a minimal application using Pyrazine
and AWS Lambda.

## Imports

We will start with the necessary imports we will use throughout the rest of the code. We will
dive deep into each of these objects once we need to use them.

```python
from pyrazine.auth import CognitoAuthorizer, DDBAuthStorage
from pyrazine.auth.simpleuserprofile import SimpleUserProfile
from pyrazine.handlers import ApiGatewayEventHandler
from pyrazine.jwt import JwtToken
from pyrazine.requests import HttpRequest
from pyrazine.response import HttpResponse
```

## Create the event handler.

To handle the incoming API Gateway events, we will create an ApiGatewayEventHandler
object. Unless you want to override its default behavior, this handler only needs to
be told how to authorize requests, i.e.: how to validate the tokens it receives from
your users.

We will use the `CognitoAuthorizer` that ships with Pyrazine, which users an Amazon
Cognito user pool to handle authentication, and knows how to validate the tokens issued
by Cognito.

The `auth_storage` parameter passed to the authorizer tells the authorizer how to read
and write user profile data. Pyrazine has a simple but effective storage implementation
based on Amazon DynamoDB called `DDBAuthStorage`, but you can write your own, if you
need more complex features. Profile data is mapped to a class which you specify in the
`user_profile_cls` parameter.

```python
handler = ApiGatewayEventHandler(
    authorizer=CognitoAuthorizer(
        user_pool_id='eu-west-1_hxZrVG3Iv',
        client_ids=('1fcrh8i1b13uv2il8or846kb3',),
        region='eu-west-1',
        auth_storage=DDBAuthStorage(
            user_table_name='pyrazine_users',
            user_profile_cls=SimpleUserProfile)
        ),
    )
```

Now that we have got the handler, we are ready to start implementing our minimal application.

## Create the handler for the GET method.

The handler for our Hello World application is quite simple.

```python
@handler.route(path='/')
def hello_world(request: HttpRequest):
    return HttpResponse(200, {'result': 'Hello, world!'})
```

Let us see what each line does:

 * First, a route handler is defined by annotating the `hello_world` function with the `@handler.route(path='/')`
   attribute. This tells Pyrazine that, whenever a HTTP request is received for the endpoint at path
   `/`, it should be forwarded to this method for processing.
   
 * The `hello_world` function takes three arguments: `token`, `body`, and `context`:
   * The `token` argument is always an object that inherits the `JwtToken` class, which stores the
     contents of the JWT token passed to the Lambda function. If you are using a `CognitoAuthorizer`
     then the contents of `token` are of type `CognitoJwtToken`.
 