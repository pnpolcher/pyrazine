## Authorizer

### The `authorizer` method

The authorizer method's main use is to verify whether a user is authorizer to invoke a given
endpoint. Since roles are stored in the user profile by design, a side effect of the authorizer
that can be put to good use is to make the user profile information available to associated
endpoint without having to make a second query. Although of limited use (not *every* endpoint
needs this information), there is no point in keeping the data for the authorizer, only.

The `authorizer` method should also expect a series of variables in its authorization context.
Pyrazine-compliant authorizers should expect at least the following ones:

* `fetch_full_profile` Instruct the authorizer to retrieve the full profile. By default, an
authorizer should only retrieve the user's permissions information.
  
### `CognitoAuthorizer`

The `CognitoAuthorizer` class implements a very simple authorizer that verifies a user identity
and permissions with the aid of an Amazon Cognito Access Token. Profile information is retrieved
using an implementation of the `BaseAuthStorage` class. Provided with Pyrazine are the following
storage backends:

* `DDBAuthStorage` Stores the user profile in a DynamoDB table.


