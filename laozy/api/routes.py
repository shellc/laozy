import time
from starlette.authentication import requires
from fastapi import Request, HTTPException
from pydantic import BaseModel

from .entry import entry
from ..db import channel_routes
from ..utils import uuid

@entry.get('/routes')
@requires(['authenticated'])
async def list_routes(request: Request):
    routes = await channel_routes.list_by_owner(request.user.userid)
    return routes

class RouteModel(BaseModel):
    name: str
    connector: str
    connector_id: str
    channel_id: str

@entry.post('/routes', status_code=201)
@requires(['authenticated'])
async def create(route: RouteModel, request: Request):
    r = {
        'name': route.name,
        'connector': route.connector,
        'connector_id': route.connector_id,
        'channel_id': route.channel_id,
        'owner': request.user.userid,
        'created_time': int(time.time())
    }
    await channel_routes.create(**r)
    return r

@entry.put('/routes/{connector}/{connector_id}', status_code=201)
@requires(['authenticated'])
async def update(connector:str, connector_id:str, route: RouteModel, request: Request):
    r = await channel_routes.get_route(connector, connector_id)
    if not r:
        raise HTTPException(404, "Not found.")
    
    r2u = {
        'name': route.name,
        'connector': route.connector,
        'connector_id': route.connector_id,
        'channel_id': route.channel_id,
    }
    await channel_routes.update_route(**r2u)
    
    return r2u

@entry.delete('/routes/{connector}/{connector_id}', status_code=204)
@requires(['authenticated'])
async def delete(connector:str, connector_id:str, request: Request):
    await channel_routes.delete_route(connector=connector, connector_id=connector_id)