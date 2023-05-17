import databases
import sqlalchemy
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
