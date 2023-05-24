from .base_knowledge_base import Embeddings
from chromadb.utils import embedding_functions

class HuggingFaceEmbeddings(Embeddings):
    def __init__(self, model_name='ganymedenil/text2vec-large-chinese') -> None:
        super().__init__()
        self.model_name = model_name
        self.transformer = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=self.model_name)

    def embed(self, s: str):
        es = self.transformer([s])
        if es and len(es) > 0:
            return es[0]