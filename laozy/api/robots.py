import time
from typing import Union
from starlette.authentication import requires
from fastapi import Request, HTTPException
from pydantic import BaseModel

from .entry import entry
from ..db import robots
from ..utils import uuid

@entry.get('/robots', tags=['Robot'])
@requires(['authenticated'])
async def list_robots(request: Request):
    return await robots.list_by_owner(request.user.userid)

@entry.get('/robots/{id}', tags=['Robot'])
@requires(['authenticated'])
async def get_robot(id:str, request: Request):
    return await robots.get(id)

class RobotModel(BaseModel):
    name: str
    implement: str
    prompt_template_id:str
    variables: str
    knowledge_base_id: Union[str, None] = None

@entry.post('/robots', status_code=201, tags=['Robot'])
@requires(['authenticated'])
async def create_robot(robot: RobotModel, request: Request):
    r = {
        'id': uuid(),
        'name': robot.name,
        'implement': robot.implement,
        'prompt_template_id': robot.prompt_template_id,
        'variables': robot.variables,
        'knowledge_base_id': robot.knowledge_base_id,
        'owner': request.user.userid,
        'created_time': int(time.time())
    }
    await robots.create(**r)
    return r

@entry.put('/robots/{id}', status_code=201, tags=['Robot'])
@requires(['authenticated'])
async def modify_robot(id:str, robot: RobotModel, request: Request):
    r = await robots.get(id)
    if not r:
        raise HTTPException(404, "Not found.")
    
    r2u = {
        'name': robot.name,
        'implement': robot.implement,
        'prompt_template_id': robot.prompt_template_id,
        'variables': robot.variables,
        'knowledge_base_id': robot.knowledge_base_id
    }
    await robots.update(id, **r2u)
    r2u['id'] = r.id
    return r2u

@entry.delete('/robots/{id}', status_code=204, tags=['Robot'])
@requires(['authenticated'])
async def remove_robot(id:str, request: Request):
    await robots.delete(id)