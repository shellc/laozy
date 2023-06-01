import os
from .base_knowledge_base import Knowledge, Embeddings, KnowledgeBase
from .chroma_knowledge_base import ChromaKnowledgeBase
from .sqlite_vss_knowledge_base import SqliteVssKnowledgeBase

from .openai_embeddings import OpenAIEmbeddings
from .sentence_transformer_embeddings import SentenceTransformerEmbeddings
from .. import settings

knowledge_base: KnowledgeBase = None
embeddings: Embeddings = None

vector_search_engine = settings.get('VECTOR_SEARCH_ENGINE')
if 'chromadb' == vector_search_engine:
    knowledge_base = ChromaKnowledgeBase(persist_dir=os.sep.join([settings.home(), 'chromadb']))
elif 'sqlite-vss' == vector_search_engine:
    knowledge_base = SqliteVssKnowledgeBase(persist_dir=os.sep.join([settings.home(), 'sqlite-vss']))

embeddings_impl = settings.get('EMBEDDINGS')
if 'sentence-transformers' == embeddings_impl:
    embeddings = SentenceTransformerEmbeddings()
elif 'openai' == embeddings_impl:
    embeddings = OpenAIEmbeddings()
