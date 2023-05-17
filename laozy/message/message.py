import uuid
import time
from pydantic import BaseModel, validator
from typing import Union, AsyncIterator
import asyncio


class Message(BaseModel):
    id: str = uuid.uuid1().hex
    connector: Union[str, None] = None
    connector_id: str
    connector_userid: str
    connector_msgid: Union[str, None] = None
    channel_id: Union[str, None] = None
    robot_id: Union[str, None] = None
    direction: int = 0
    send_time: int = int(time.time())
    msgtype: str = 'text'
    content: str
    status: int = 0
    created_time: int = int(time.time())

    streaming: bool = False

    event: asyncio.Event = None
    streaming_iter: AsyncIterator = None
    
    class Config:
        arbitrary_types_allowed = True
        fields = {
            'streaming': {
                'exclude': ...,
            },
            'event': {
                'exclude': ...,
            },
            'streaming_iter': {
                'exclude': ...,
            }
        }

    @validator('event')
    def v_event(cls, event: asyncio.Event):
        return event
