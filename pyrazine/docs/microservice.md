# Writing a microservice using Pyrazine

## Create the event handler.

To handle the incoming API Gateway events, create an ApiGatewayEventHandler object. 

```
handler = ApiGatewayEventHandler(
    authorizer=CognitoAuthorizer(
        user_pool_id='eu-west-1_hxZrVG3Iv',
        client_id='1fcrh8i1b13uv2il8or846kb3',
        region='eu-west-1',
        auth_storage=DDBAuthStorage(
            user_table_name='pyrazine_users',
            user_profile_cls=SimpleUserProfile)
        ),
    )
```