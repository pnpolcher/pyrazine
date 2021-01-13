# Pyrazine

Library under development

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
