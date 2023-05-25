import databases
import sqlalchemy

from .db import Model, create_pydantic_model
from .db import metadata
from .db import instance as db
from ..utils import uuid


class MessageModel(Model):
    def __init__(self, name, metadata: sqlalchemy.MetaData, db: databases.Database, *args) -> None:
        super().__init__(name, metadata, db, *args)

    async def get_history(self, connector, connector_id, connector_userid, channel_id, last=10):
        q = self.table.select().where(messages.c.connector == connector, messages.c.connector_id == connector_id,
                                messages.c.connector_userid == connector_userid, messages.c.channel_id == channel_id).order_by(messages.c.created_time.desc()).limit(last)
        return await self.db.fetch_all(q)

    async def save(self, **kwargs):
        q = self.table.insert().values(**kwargs)
        await self.db.execute(q)

    async def truncate(self):
        q = self.table.delete()
        await self.db.execute(q)


messages = MessageModel(
    'messages',
    metadata,
    db,
    sqlalchemy.Column('id', sqlalchemy.String(50), primary_key=True),
    sqlalchemy.Column('connector', sqlalchemy.String(50), index=True),
    sqlalchemy.Column('connector_id', sqlalchemy.String(50), index=True),
    sqlalchemy.Column('connector_userid', sqlalchemy.String(50), index=True),
    sqlalchemy.Column('connector_msgid', sqlalchemy.String(50), index=True),
    sqlalchemy.Column('channel_id', sqlalchemy.String(50), index=True),
    sqlalchemy.Column('robot_id', sqlalchemy.String(50), index=True),
    sqlalchemy.Column('direction', sqlalchemy.Integer, index=True),
    sqlalchemy.Column('send_time', sqlalchemy.Integer, index=True),
    sqlalchemy.Column('created_time', sqlalchemy.Integer, index=True),
    sqlalchemy.Column('msgtype', sqlalchemy.String(20)),
    sqlalchemy.Column('content', sqlalchemy.String(4096)),
    sqlalchemy.Column('status', sqlalchemy.Integer, index=True),
)

MessagePdModel = create_pydantic_model(messages)