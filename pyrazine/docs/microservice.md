# Writing a microservice using Pyrazine

## Introduction

As a first exercise to understand the basics of Pyrazine, we will create
a microservice to read the notes that our users store in the application.

## Imports

We will start with the necessary imports we will use throughout the rest of
the code.

```python
from pyrazine.auth import CognitoAuthorizer, DDBAuthStorage
from pyrazine.handlers import ApiGatewayEventHandler
from pyrazine.jwt import JwtToken
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

Now that we have got the handler, we are ready to start implementing our microservice.

## Create the handler method for GET requests.

We want our users to be able to fetch the notes they've written, as well as to store new
notes. We'll split this functionality into three methods:

### Read method

```python
@handler.route(path='/notes', methods=('GET',), roles=('admin', 'user'))
def get_items(token: JwtToken, body: Dict[str, Any], context: RequestContext):
    pass
```

### Create/update method

```python
@handler.route(path='/notes', methods=('POST', 'PUT'), roles=('admin', 'user'))
def put_items(token: JwtToken, body: Dict[str, Any], context: RequestContext):
    pass
```

### Delete method

```python
@handler.route(path='/notes', methods=('DELETE',), roles=('admin', 'user'))
def delete_item(token: JwtTOken, body: Dict[str, Any], context: RequestContext):
    pass
```
