import sqlalchemy

from .db import metadata
from .db import instance as db

robots = sqlalchemy.Table(
    'robots',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.String(50), primary_key=True),
    sqlalchemy.Column('implement', sqlalchemy.String(50)),
    sqlalchemy.Column('name', sqlalchemy.String(50)),
    sqlalchemy.Column('prompt_template_id', sqlalchemy.String(50)),
    sqlalchemy.Column('variables', sqlalchemy.String(4096)),
    sqlalchemy.Column('owner', sqlalchemy.String(50), index=True),
    sqlalchemy.Column('created_time', sqlalchemy.Integer, index=True),
)

async def all():
    q = robots.select()
    return await db.fetch_all(q)

async def get(id: str):
    q = robots.select(robots.c.id == id)
    return await db.fetch_one(q)