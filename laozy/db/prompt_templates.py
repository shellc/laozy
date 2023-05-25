import databases
import sqlalchemy

from .db import Model
from .db import metadata, create_pydantic_model
from .db import instance as db
from ..utils import uuid

class PromptTemplatesModel(Model):
    def __init__(self, name, metadata: sqlalchemy.MetaData, db: databases.Database, *args) -> None:
        super().__init__(name, metadata, db, *args)

    async def getbyowner(self, owner):
        q = self.table.select().where(self.c.owner == owner).order_by(self.c.created_time.desc())
        return await self.db.fetch_all(q)

prompt_templates = PromptTemplatesModel(
    'prompt_templates',
    metadata,
    db,
    sqlalchemy.Column('id', sqlalchemy.String(50), primary_key=True),
    sqlalchemy.Column('name', sqlalchemy.String(50)),
    sqlalchemy.Column('template', sqlalchemy.String(4096)),
    sqlalchemy.Column('variables', sqlalchemy.String(4096)),
    sqlalchemy.Column('owner', sqlalchemy.String(50), index=True),
    sqlalchemy.Column('created_time', sqlalchemy.Integer, index=True),
)

PromptTemplatesPdModel = create_pydantic_model(prompt_templates)