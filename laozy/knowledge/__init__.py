import os
from .base_knowledge_base import Knowlege, Embeddings, KnowledgeBase
from .chroma_knowledge_base import ChromaKnowledgeBase

from .openai_embeddings import OpenAIEmbeddings
from .sentence_transformer_embeddings import SentenceTransformerEmbeddings
from .. import settings

knowledge_base: KnowledgeBase = ChromaKnowledgeBase(
    persist_dir=os.sep.join([settings.home(), 'chromadb']))

embeddings: Embeddings = SentenceTransformerEmbeddings()
