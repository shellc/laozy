import json
from .entry import entry

from ..db import MessagePdModel

@entry.post('/messages/labels', tags=['Message'])
async def labeled_message(message: MessagePdModel):
    chars = 0
    if message.content:
        chars = len(message.content)
    message.extra = json.dumps({'characters': chars})
    return message