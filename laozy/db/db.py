from typing import Optional
import databases
import sqlalchemy
from pydantic import BaseConfig, BaseModel, create_model

from .. import settings

# Database table definitions
metadata = sqlalchemy.MetaData()

database_url = settings.get('DATABASE_URL')
if not database_url:
    database_url = "/".join(['sqlite+aiosqlite://',
                             settings.home(), 'laozy.db'])

instance = databases.Database(database_url)


class Model:
    def __init__(self, name, metadata: sqlalchemy.MetaData, db: databases.Database, *args) -> None:
        self.name = name
        self.metadata = metadata
        self.db = db

        self.table = sqlalchemy.Table(self.name, self.metadata, *args)
        self.c = self.table.c

    def select(self):
        return self.table.select()

    async def get_one(self, query):
        return await self.db.fetch_one(query)

    async def iterate(self, query):
        return await self.db.iterate(query=query)

    async def create(self, **kwargs):
        q = self.table.insert().values(**kwargs)
        return await self.db.execute(q)

    async def get(self, id):
        q = self.table.select().where(self.c['id'] == id).limit(1)
        return await self.db.fetch_one(q)
    
    async def update(self, id, **values):
        q = self.table.update().where(self.c.id == id).values(**values)
        return await self.db.execute(q)
    
    async def delete(self, id):
        q = self.table.delete().where(self.c.id == id)
        return await self.db.execute(q)
    
    async def all(self):
        q = self.table.select()
        return await self.db.fetch_all(q)
    
    async def list_by_owner(self, owner):
        q = self.table.select().where(self.c.owner == owner).order_by(self.c.created_time.desc())
        return await self.db.fetch_all(q)

def create_pydantic_model(model: Model):
    fields = {}
    for c in model.table.columns:
        pdtype = None
        ptype = None
        t = str(c.type)
        if t.startswith('VARCHAR'):
            ptype = str
        elif t.startswith('INT'):
            ptype = int
        else:
            raise ValueError('Type unsupported %s ' % c.type)
        
        if c.nullable:
            pdtype = Optional[ptype]
        else:
            pdtype = ptype

        fields[str(c.name)] = (pdtype, c.default)
        
    pydantic_model = create_model(__model_name=model.__class__.__name__, **fields)
    return pydantic_model
