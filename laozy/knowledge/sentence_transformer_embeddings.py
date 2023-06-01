from .base_knowledge_base import Embeddings
from chromadb.utils import embedding_functions
from .. import settings


class SentenceTransformerEmbeddings(Embeddings):
    def __init__(self, model_name=None) -> None:
        super().__init__()
        self.model_name = model_name

        if not model_name:
            self.model_name = settings.get('SENTENCE_TRANSFORMERS_MODEL_NAME')

        if not self.model_name:
            self.model_name = 'ganymedenil/text2vec-large-chinese'

        self.transformer = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=self.model_name)

    def embed(self, s: str):
        es = self.transformer([s])
        if es and len(es) > 0:
            return es[0]
