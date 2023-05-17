from starlette.authentication import requires
from fastapi import Request

from . import entry
from ..db import channel_routes

@entry.get('/routes')
@requires(['authenticated'])
async def list_routes(request: Request):
    print(request.user.userid)
    routes = await channel_routes.list_routes(request.user.userid)
    return routes