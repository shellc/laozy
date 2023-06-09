from typing import List
import time
from starlette.authentication import requires
from fastapi import Request, HTTPException
from pydantic import BaseModel

from .entry import entry
from ..db import channels, ChannelRoutesPdModel, ChannelsPdModel
from ..utils import uuid


@entry.get('/channels', tags=['Channel'])
@requires(['authenticated'])
async def list_channels(request: Request) -> List[ChannelsPdModel]:
    return await channels.list_by_owner(request.user.userid)


class ChannelModel(BaseModel):
    name: str
    robot_id: str


@entry.post('/channels', status_code=201, tags=['Channel'])
@requires(['authenticated'])
async def create_channel(ch: ChannelModel, request: Request) -> ChannelsPdModel:
    r = ChannelsPdModel(
        id=uuid(),
        name=ch.name,
        robot_id=ch.robot_id,
        owner=request.user.userid,
        created_time=int(time.time())
    )

    await channels.create(**r.dict())
    return r


@entry.put('/channels/{id}', status_code=201, tags=['Channel'])
@requires(['authenticated'])
async def modify_channel(id: str, ch: ChannelModel, request: Request) -> ChannelsPdModel:
    r = await channels.get(id)
    if not r:
        raise HTTPException(404, "Not found.")

    r2u = {
        'name': ch.name,
        'robot_id': ch.robot_id,
    }
    
    await channels.update(id, **r2u)
    
    r.name = ch.name
    r.robot_id = ch.robot_id
    return r


@entry.delete('/channels/{id}', status_code=204, tags=['Channel'])
@requires(['authenticated'])
async def remove_channel(id: str, request: Request):
    await channels.delete(id)
