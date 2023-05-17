import sqlalchemy

from .db import metadata
from .db import instance as db

prompt_templates = sqlalchemy.Table(
    'prompt_templates',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.String(50), primary_key=True),
    sqlalchemy.Column('template', sqlalchemy.String(4096)),
    sqlalchemy.Column('variables', sqlalchemy.String(50), primary_key=True),
    sqlalchemy.Column('name', sqlalchemy.String(50)),
    sqlalchemy.Column('owner', sqlalchemy.String(50), index=True),
    sqlalchemy.Column('created_time', sqlalchemy.Integer, index=True),
)

async def all():
    q = prompt_templates.select()
    return await db.fetch_all(q)

async def get(id: str):
    q = prompt_templates.select(prompt_templates.c.id == id)
    return await db.fetch_one(q)