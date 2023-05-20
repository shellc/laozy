from typing import Union
import chromadb
from chromadb.config import Settings

from laozy.knowledge.base_knowledge_base import Knowlege

from .base_knowledge_base import KnowledgeBase
from ..utils import uuid


class ChromaKnowledgeBase(KnowledgeBase):
    def __init__(self, persist_dir: str) -> None:
        super().__init__()

        self.client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=persist_dir
        ))

    async def save(self, collection: str, k: Knowlege):
        col = self.client.get_or_create_collection(name=collection)
        req = {
            'documents': [k.content],
            'ids': [uuid()]
        }
        if k.tag:
            req['metadatas'] = [{"tag": k.tag}]

        col.add(**req)

    async def retrieve(self, collection: str, content: str, tag: str | None = None, topk=10):
        col = self.client.get_or_create_collection(name=collection)
        req = {
            'query_texts': [content],
            'n_results': topk
        }
        if tag:
            req['where'] = {"tag": tag}

        result = None
        try:
            result = col.query(**req)
        except chromadb.errors.NotEnoughElementsException as e:
            req['n_results'] = col.count()
            if req['n_results'] > 0:
                result = col.query(**req)

        ret = []
        if result:
            #print(result)
            ids = result['ids']
            docs = result['documents']
            for i in range(len(docs[0])):
                ret.append(Knowlege(id=ids[0][i], content=docs[0][i]))

        return ret
    
    async def delete(self, collection: str, id: str):
        col = self.client.get_or_create_collection(name=collection)
        col.delete(ids=[id])
