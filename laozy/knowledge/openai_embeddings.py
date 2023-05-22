from langchain.embeddings import OpenAIEmbeddings as _OpenAIEmbeddings
from .base_knowledge_base import Embeddings

from .. import settings

class OpenAIEmbeddings(Embeddings):
    def __init__(self) -> None:
        super().__init__()
        self.embeddings = _OpenAIEmbeddings(
            openai_api_base=settings.get('OPENAI_API_BASE'),
            openai_api_key=settings.get('OPENAI_API_KEY'),
            openai_api_version='2020-11-07',
            )

    def embed(self, s: str):
        return self.embeddings.embed_query(s)

