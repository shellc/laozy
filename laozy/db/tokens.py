import databases
import sqlalchemy

from .db import Model
from .db import metadata
from .db import instance as db
from ..utils import uuid

class TokenModel(Model):
    def __init__(self, name, metadata: sqlalchemy.MetaData, db: databases.Database, *args) -> None:
        super().__init__(name, metadata, db, *args)

tokens = TokenModel(
    'tokens',
    metadata,
    db,
    sqlalchemy.Column('id', sqlalchemy.String(50), primary_key=True),
    sqlalchemy.Column('userid', sqlalchemy.String(50), index=True),
    sqlalchemy.Column('created_time', sqlalchemy.Integer, index=True),
    sqlalchemy.Column('expires_at', sqlalchemy.Integer, index=True),
)