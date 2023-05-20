from typing import Union
from pydantic import BaseModel


class Knowlege(BaseModel):
    id: Union[str, None] = None
    content: str
    tag: Union[str, None] = None


class KnowledgeBase:
    async def save(self, collection: str, k: Knowlege):
        pass

    async def retrieve(self, collection: str, content: str, tag: Union[str, None] = None):
        pass

    async def delete(self, collection: str, id: str):
        pass
