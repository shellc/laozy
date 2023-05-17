import sqlalchemy

from .db import metadata
from .db import instance as db

messages = sqlalchemy.Table(
    'messages',
    metadata,
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


async def truncate():
    q = messages.delete()
    await db.execute(q)


async def save(**kwargs):
    q = messages.insert().values(**kwargs)
    await db.execute(q)


async def get_history(connector, connector_id, connector_userid, channel_id, last=10):
    q = messages.select().where(messages.c.connector == connector, messages.c.connector_id == connector_id,
                                messages.c.connector_userid == connector_userid, messages.c.channel_id == channel_id).order_by(messages.c.created_time.desc()).limit(last)
    return await db.fetch_all(q)
