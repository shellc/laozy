import databases
import sqlalchemy

from .db import Model
from .db import metadata, create_pydantic_model
from .db import instance as db
from ..utils import uuid

class KnowledgeModel(Model):
    def __init__(self, name, metadata: sqlalchemy.MetaData, db: databases.Database, *args) -> None:
        super().__init__(name, metadata, db, *args)

knowledges = KnowledgeModel(
    'knowledges',
    metadata,
    db,
    sqlalchemy.Column('id', sqlalchemy.String(50), primary_key=True),
    sqlalchemy.Column('name', sqlalchemy.String(50)),
    sqlalchemy.Column('owner', sqlalchemy.String(50), index=True),
    sqlalchemy.Column('created_time', sqlalchemy.Integer, index=True),
)

KnowledgePdModel = create_pydantic_model(knowledges)