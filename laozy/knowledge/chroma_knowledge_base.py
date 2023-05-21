from typing import Union, Dict, List
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

    async def save(self, collection: str, knowledges: List[Knowlege]):
        col = self.client.get_or_create_collection(name=collection)
        documents = []
        ids = []
        metadatas = []

        for k in knowledges:
            documents.append(k.content)
            ids.append(k.id if k.id else uuid())
            metadatas.append(k.metadata if k.metadata else {})

        req = {
            'documents': documents,
            'ids': ids,
            'metadatas': metadatas
        }

        await col.add(**req)

    async def retrieve(self, collection: str, content: str, metadata: Union[Dict, None] = None, topk=10):
        col = self.client.get_or_create_collection(name=collection)
        req = {
            'query_texts': [content],
            'n_results': topk
        }
        if metadata:
            req['where'] = metadata

        result = None
        try:
            result = await col.query(**req)
        except chromadb.errors.NotEnoughElementsException as e:
            req['n_results'] = col.count()
            if req['n_results'] > 0:
                result = col.query(**req)
        except chromadb.errors.NoDatapointsException as e:
            pass

        ret = []
        if result:
            #print(result)
            ids = result['ids']
            docs = result['documents']
            metadatas = result['metadatas']
            distances = result['distances']
            for i in range(len(docs[0])):
                ret.append(Knowlege(id=ids[0][i], content=docs[0][i], metadata=metadatas[0][i], distance=distances[0][i]))

        return ret
    
    async def delete(self, collection: str, id: str):
        col = self.client.get_or_create_collection(name=collection)
        await col.delete(ids=[id])
