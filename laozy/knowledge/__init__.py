import os
from .base_knowledge_base import Knowlege
from .chroma_knowledge_base import ChromaKnowledgeBase

from .. import settings

knowledge_base = ChromaKnowledgeBase(persist_dir=os.sep.join([settings.home(), 'chromadb']))