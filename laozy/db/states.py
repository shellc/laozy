import sqlalchemy

from .db import metadata
from .db import instance as db

states = sqlalchemy.Table(
    'states',
    metadata,
    sqlalchemy.Column('key', sqlalchemy.String(50), primary_key=True),
    sqlalchemy.Column('value', sqlalchemy.String(50)),
)

async def get_state(key: str):
    q = states.select().where(states.c.key == key)
    r = await db.fetch_one(q)

    return r.value if r else None

async def set_state(key: str, value: str):
    # async with self.database.transaction():
    v = await get_state(key)
    q = None
    if v:
        q = states.update().where(states.c.key == key).values(value=value)
    else:
        q = states.insert().values(key=key, value=value)
    await db.execute(q)
