from typing import Union, Dict, List
import chromadb
from chromadb.config import Settings
from chromadb.api.types import Documents, EmbeddingFunction, Embeddings as chromadb_Embeddings

from laozy.knowledge.base_knowledge_base import Knowlege

from .base_knowledge_base import KnowledgeBase, Embeddings
from ..utils import uuid

from ..logging import log

def embedding_wrapper(embeddings: Embeddings):
    class WrapperedEmbeddingFunction(EmbeddingFunction):
        def __call__(self, texts: Documents) -> chromadb_Embeddings:
            ret = []
            for d in texts:
                ret.append(embeddings.embed(d))

            return ret
        
    return WrapperedEmbeddingFunction()

class ChromaKnowledgeBase(KnowledgeBase):
    def __init__(self, persist_dir: str) -> None:
        super().__init__()

        self.client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=persist_dir
        ))

    async def create(self, collection: str, embeddings: Embeddings = None):
        self.client.create_collection(name=collection, embedding_function=embedding_wrapper(embeddings))

    async def save(self, collection: str, knowledges: List[Knowlege], embeddings: Embeddings = None):
        col = self.client.get_or_create_collection(name=collection, embedding_function=embedding_wrapper(embeddings))
        documents = []
        ids = []
        metadatas = []
        embds = []

        for k in knowledges:
            documents.append(k.content)
            ids.append(k.id if k.id else uuid())
            metadatas.append(k.metadata if k.metadata else {})
            embds.append(k.embeddings if k.embeddings else [])

        req = {
            'documents': documents,
            'ids': ids,
            'metadatas': metadatas,
            'embeddings': embds
        }

        col.add(**req)

    async def retrieve(self, collection: str, content: str, metadata: Union[Dict, None] = None, topk=10, embeddings: Embeddings = None):
        col = self.client.get_collection(name=collection, embedding_function=embedding_wrapper(embeddings))
        if len(content) < 1:
            content = ' '
        req = {
            'query_texts': [content],
            'n_results': topk
        }

        if metadata:
            req['where'] = metadata

        result = None
        try:
            result = col.query(**req)
        except chromadb.errors.NotEnoughElementsException as e:
            req['n_results'] = col.count()
            if req['n_results'] > 0:
                result = col.query(**req)
        except chromadb.errors.NoDatapointsException as e:
            pass
        except chromadb.errors.NoIndexException as e:
            log.warning(e)

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
        col = self.client.get_collection(name=collection)
        col.delete(ids=[id])

    async def drop(self, collection: str):
        return self.client.delete_collection(collection)
