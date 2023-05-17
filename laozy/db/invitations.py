import databases
import sqlalchemy

from .db import Model
from .db import metadata
from .db import instance as db
from ..utils import uuid

class InvitationModel(Model):
    def __init__(self, name, metadata: sqlalchemy.MetaData, db: databases.Database, *args) -> None:
        super().__init__(name, metadata, db, *args)

    async def invalid(self, id):
        q = self.table.update().where(self.c.id == id).values(invalid=True)
        await self.db.execute(q)


invitations = InvitationModel(
    'invitations',
    metadata,
    db,
    sqlalchemy.Column('id', sqlalchemy.String(50), primary_key=True),
    sqlalchemy.Column('invalid', sqlalchemy.Boolean, index=True, default=False),
    sqlalchemy.Column('created_time', sqlalchemy.Integer),
)
