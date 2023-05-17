import uuid,time
from .base_connector import Connector
from ..message import Message


class WebConnector(Connector):

    async def receive(self, msg: Message):
        msg.connector = 'web'
        msg.id = uuid.uuid1().hex
        msg.send_time = int(time.time())
        msg.created_time = msg.send_time
        msg.connector_msgid = msg.id
        msg.direction = 0
        msg.msgtype = 'text'
        msg.status = 0
        
        await self.received.put(msg)