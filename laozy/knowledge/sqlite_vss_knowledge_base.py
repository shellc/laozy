import os, json
from typing import Optional, List, Dict
from .base_knowledge_base import Embeddings, Knowledge, KnowledgeBase

import sqlite_vss
import sqlite3
from ..utils import uuid
from ..logging import log

import numpy
def tobytes(l):
    return numpy.asarray(l, dtype='float32').tobytes()

class SqliteVssKnowledgeBase(KnowledgeBase):
    def __init__(self, persist_dir) -> None:
        super().__init__()
        self.persist_dir = persist_dir
        if not os.path.exists(self.persist_dir):
            os.mkdir(self.persist_dir)
        self.db_file = os.path.sep.join([self.persist_dir, 'vss.db'])
        
        self.db = sqlite3.connect(self.db_file)
        self.db.enable_load_extension(True)
        sqlite_vss.load(self.db)
        vss_version = self.db.execute('select vss_version()').fetchone()[0]
        log.info('SQLite VSS Version: %s' % vss_version)

    async def create(self, collection: str, embeddings: Embeddings = None):
        dim = len(embeddings.embed('test'))
        create_sql = """
            CREATE TABLE data_%s (
                id VARCHAR(100) PRIMARY KEY NOT NULL,
                content TEXT,
                meta TEXT,
                embeddings FVECTOR
            )
        """ % collection
        self.db.execute(create_sql)
        self.db.execute('create virtual table vss_%s using vss0 (embeddings(%d))' % (collection, dim))
        trigger_i_sql = """
            CREATE TRIGGER trigger_i_%s AFTER INSERT ON data_%s BEGIN
            INSERT INTO vss_%s(rowid, embeddings) VALUES (new.rowid, new.embeddings);
            END;
        """ % (collection, collection, collection)
        self.db.execute(trigger_i_sql)

        trigger_d_sql = """
            CREATE TRIGGER trigger_d_%s AFTER DELETE ON data_%s BEGIN
            DELETE FROM vss_%s WHERE rowid=old.rowid;
            END;
        """ % (collection, collection, collection)
        self.db.execute(trigger_d_sql)

        trigger_u_sql = """
            CREATE TRIGGER trigger_u_%s AFTER UPDATE ON data_%s BEGIN
            UPDATE vss_%s SET embeddings=new.embeddings;
            END;
        """ % (collection, collection, collection)
        self.db.execute(trigger_u_sql)

    async def save(self, collection: str, knowledges: List[Knowledge], embeddings: Embeddings = None):
        cur = self.db.cursor()
        try:
            for k in knowledges:
                if not k.id:
                    k.id = uuid()
                if not k.metadata:
                    k.metadata = {}

                sql = "insert into data_%s (id, content, meta, embeddings) values (?,?,?,?)" % collection
                e = k.embeddings
                if not e:
                    e = embeddings.embed(k.content)
                cur.execute(sql, (k.id, k.content, json.dumps(k.metadata), tobytes(e)))
                self.db.commit()
        finally:
            cur.close()

    async def retrieve(self, collection: str, content: Optional[str] = None, metadata: Optional[Dict] = None, topk=10, embeddings: Embeddings = None):
        sql = """
            select rowid, distance from vss_%s where vss_search(embeddings, ?) order by distance desc limit ?
        """ % collection

        e = embeddings.embed(content)
        knowledges = []
        cur = self.db.cursor()
        try:
            rows = cur.execute(sql, (tobytes(e), topk)).fetchall()
            rowids = {}
            for r in rows:
                rowids[r[0]] = r[1]
            placeholders = ','.join('?' for i in list(rowids.keys()))
            rows = cur.execute("select rowid, id, content, meta from data_%s where rowid in (%s)" % (collection, placeholders), tuple(rowids.keys()))
            for r in rows:
                knowledges.append(Knowledge(
                    id=r[1],
                    content=r[2],
                    metadata=json.loads(r[3]),
                    distance=rowids[r[0]]
                    ))
        finally:
            cur.close()
        return sorted(knowledges, key=lambda x : x.distance)

    async def delete(self, collection: str, id: str):
        cur = self.db.cursor()
        try:
            cur.execute("DELETE FROM data_%s WHERE id=:id" % collection, {'id':id})
        finally:
            cur.close()

    async def drop(self, collection: str):
        self.db.execute("drop table if exists vss_%s" % collection)
        self.db.execute("drop table if exists data_%s" % collection)
        self.db.execute("drop trigger if exists trigger_i_%s" % collection)
        self.db.execute("drop trigger if exists trigger_d_%s" % collection)
        self.db.execute("drop trigger if exists trigger_u_%s" % collection)
