# Pyrazine

Library under development

## Motivation

There are tons of libraries and frameworks out there that provide foundations for solid applications.
Not all of them are suited for serverless applications, though, and adaptations to use these frameworks
on serverless compute environments, like AWS Lambda, either result in complex workarounds that were
never meant to be, or they add enough complexity to deter their use in small projects and proof of
concepts.

Pyrazine aims to be a simple, unopinionated library that eliminates much of the complexity and boilerplate
code by providing simple wrappers and features to accelerate the development and deployment of serverless
applications, while keeping it simple enough for developers to learn it quickly and get productive
in a matter of hours.

## Example

```python
from typing import Dict

from pyrazine.handlers import LambdaHandler
from pyrazine.jwt import JwtToken
from pyrazine.response import HttpResponse

handler = LambdaHandler()


@handler.route(path='/', methods=('GET',), trace=True)
def route_handler(token: JwtToken, body: Dict[str, object]) -> HttpResponse:
    # Do something and then return a response.
    return HttpResponse(200, body={'hello': 'world'})
```
