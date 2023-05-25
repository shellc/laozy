import time
from typing import Union, Optional, List
from starlette.authentication import requires
from fastapi import Request, HTTPException
from pydantic import BaseModel

from .entry import entry
from ..db import robots, RobotPdModel
from ..utils import uuid

@entry.get('/robots', tags=['Robot'])
@requires(['authenticated'])
async def list_robots(request: Request) -> List[RobotPdModel]:
    return await robots.list_by_owner(request.user.userid)

@entry.get('/robots/{id}', tags=['Robot'])
@requires(['authenticated'])
async def get_robot(id:str, request: Request) -> RobotPdModel:
    return await robots.get(id)

class RobotModel(BaseModel):
    name: str
    implement: str
    prompt_template_id:str
    variables: str
    knowledge_base_id: Union[str, None] = None
    history_limit: Optional[int] = -1
    knowledge_limit: Optional[int] = -1
    knowledge_query_limit: Optional[int] = -1
    knowledge_max_length: Optional[int] = -1
    message_hook: Optional[str] = None

@entry.post('/robots', status_code=201, tags=['Robot'])
@requires(['authenticated'])
async def create_robot(robot: RobotModel, request: Request) -> RobotPdModel:
    r = robot.dict()
    r['id'] = uuid()
    r['created_time'] = int(time.time())
    r['owner'] = request.user.userid
    
    await robots.create(**r)
    return RobotPdModel(**r)

@entry.put('/robots/{id}', status_code=201, tags=['Robot'])
@requires(['authenticated'])
async def modify_robot(id:str, robot: RobotModel, request: Request) -> RobotPdModel:
    r = await robots.get(id)
    if not r:
        raise HTTPException(404, "Not found.")
    
    r2u = robot.dict()
    
    await robots.update(id, **r2u)
    r2u['id'] = r.id
    return RobotPdModel(**r2u)

@entry.delete('/robots/{id}', status_code=204, tags=['Robot'])
@requires(['authenticated'])
async def remove_robot(id:str, request: Request):
    await robots.delete(id)