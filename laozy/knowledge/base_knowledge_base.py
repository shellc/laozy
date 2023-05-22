from typing import Union, Dict, List
from pydantic import BaseModel


class Knowlege(BaseModel):
    id: Union[str, None] = None
    content: str
    metadata: Union[Dict, None] = None
    distance: Union[float, None] = None


class KnowledgeBase:
    async def save(self, collection: str, knowledges: List[Knowlege]):
        pass

    async def retrieve(self, collection: str, content: str, metadata: Union[Dict, None] = None):
        pass

    async def delete(self, collection: str, id: str):
        pass
