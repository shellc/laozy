import databases
import sqlalchemy

from .db import Model
from .db import metadata
from .db import instance as db

class ChannelsModel(Model):
    def __init__(self, name, metadata: sqlalchemy.MetaData, db: databases.Database, *args) -> None:
        super().__init__(name, metadata, db, *args)

channels = ChannelsModel(
    'channels',
    metadata,
    db,
    sqlalchemy.Column('id', sqlalchemy.String(50), primary_key=True),
    sqlalchemy.Column('owner', sqlalchemy.String(50), index=True),
    sqlalchemy.Column('name', sqlalchemy.String(50)),
    sqlalchemy.Column('robot_id', sqlalchemy.String(50)),
    sqlalchemy.Column('created_time', sqlalchemy.Integer, index=True),
)

class ChannelRoutesModel(Model):
    def __init__(self, name, metadata: sqlalchemy.MetaData, db: databases.Database, *args) -> None:
        super().__init__(name, metadata, db, *args)

    async def get_route(self, connector:str, connector_id:str):
        q = self.table.select().where(self.c.connector==connector, self.c.connector_id == connector_id)
        return await db.fetch_one(q)
    
    async def list_routes(self, owner: str):
        q = self.table.select().where(self.c.owner == owner)
        return await db.fetch_all(q)

channel_routes = ChannelRoutesModel(
    'channel_routes',
    metadata,
    db,
    sqlalchemy.Column('connector', sqlalchemy.String(50), primary_key=True),
    sqlalchemy.Column('connector_id', sqlalchemy.String(50), primary_key=True),
    sqlalchemy.Column('channel_id', sqlalchemy.String(50)),
    sqlalchemy.Column('name', sqlalchemy.String(50)),
    sqlalchemy.Column('owner', sqlalchemy.String(50), index=True),
    sqlalchemy.Column('created_time', sqlalchemy.Integer, index=True),
)
