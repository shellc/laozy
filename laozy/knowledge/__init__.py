import os
from .base_knowledge_base import Knowlege, Embeddings
from .openai_embeddings import OpenAIEmbeddings
from .chroma_knowledge_base import ChromaKnowledgeBase

from .. import settings

knowledge_base = ChromaKnowledgeBase(persist_dir=os.sep.join([settings.home(), 'chromadb']))