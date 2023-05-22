from typing import Union, Dict, List
from pydantic import BaseModel


class Embeddings:
    def embed(self, s: str):
        pass

class Knowlege(BaseModel):
    id: Union[str, None] = None
    content: str
    metadata: Union[Dict, None] = None
    distance: Union[float, None] = None


class KnowledgeBase:
    async def create(self, collection: str, embeddings: Embeddings = None):
        pass

    async def save(self, collection: str, knowledges: List[Knowlege], embeddings: Embeddings = None):
        pass

    async def retrieve(self, collection: str, content: str, metadata: Union[Dict, None] = None, embeddings: Embeddings = None):
        pass

    async def delete(self, collection: str, id: str):
        pass

    async def drop(self, collection: str):
        pass
