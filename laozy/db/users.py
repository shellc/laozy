import databases
import sqlalchemy

from .db import Model
from .db import metadata
from .db import instance as db
from ..utils import uuid

class UsersModel(Model):
    def __init__(self, name, metadata: sqlalchemy.MetaData, db: databases.Database, *args) -> None:
        super().__init__(name, metadata, db, *args)

    async def getbyusername(self, username: str):
        q = self.select().where(self.c.username == username)
        return await self.get_one(q)


users = UsersModel(
    'users',
    metadata,
    db,
    sqlalchemy.Column('id', sqlalchemy.String(50), primary_key=True),
    sqlalchemy.Column('username', sqlalchemy.String(50), index=True),
    sqlalchemy.Column('salt', sqlalchemy.String(50)),
    sqlalchemy.Column('password', sqlalchemy.String(50)),
    sqlalchemy.Column('roles', sqlalchemy.String(50)),
    sqlalchemy.Column('created_time', sqlalchemy.Integer),
)
