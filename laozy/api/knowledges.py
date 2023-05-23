import time
from typing import List, Union
from starlette.authentication import requires
from fastapi import Request, HTTPException
from pydantic import BaseModel

from .entry import entry
from ..db import knowledges
from ..knowledge import Knowlege, knowledge_base, Embeddings, OpenAIEmbeddings
from ..utils import uuid

embeddings = OpenAIEmbeddings()


@entry.get('/knowledges', tags=['Knowledge Base'])
@requires(['authenticated'])
async def list_knowledge_bases(request: Request):
    k = await knowledges.list_by_owner(request.user.userid)
    return k


class KnowledgeModel(BaseModel):
    name: str


@entry.post('/knowledges', status_code=201, tags=['Knowledge Base'])
@requires(['authenticated'])
async def create_knowledge_base(k: KnowledgeModel, request: Request):
    r = {
        'id': uuid(),
        'name': k.name,
        'owner': request.user.userid,
        'created_time': int(time.time())
    }
    await knowledge_base.create(r['id'])
    await knowledges.create(**r)
    return r


@entry.put('/knowledges/{id}', status_code=201, tags=['Knowledge Base'])
@requires(['authenticated'])
async def modify_knowledge_base(id: str, k: KnowledgeModel, request: Request):
    r = await knowledges.get(id)
    if not r:
        raise HTTPException(404, "Not found.")

    r2u = {
        'name': k.name
    }
    await knowledges.update(id, **r2u)
    r2u['id'] = r.id
    return r2u


@entry.delete('/knowledges/{id}', status_code=204, tags=['Knowledge Base'])
@requires(['authenticated'])
async def remove_knowledge_base(id: str, request: Request):
    await knowledge_base.drop(id)
    await knowledges.delete(id)

class EmbedingRequest(BaseModel):
    content: str

@entry.post('/knowledges/embeddings', status_code=200, tags=['Knowledge Base'])
@requires(['authenticated'])
async def embedding(er: EmbedingRequest, request: Request):
    return embeddings.embed(er.content)

@entry.post('/knowledges/{knowledge_id}', status_code=201, tags=['Knowledge Base'])
@requires(['authenticated'])
async def save_knowledge(knowledge_id: str, knowledges: List[Knowlege], request: Request):
    await knowledge_base.save(collection=knowledge_id, knowledges=knowledges, embeddings=embeddings)


@entry.get('/knowledges/{knowledge_id}', status_code=200, tags=['Knowledge Base'])
@requires(['authenticated'])
async def retrieve_knowledges(knowledge_id: str, content: Union[str, None] = None, tag: Union[str, None] = None, request: Request = None):
    if not content:
        content = ''
    metadata = {}
    if tag:
        metadata['tag'] = tag
    return await knowledge_base.retrieve(collection=knowledge_id, content=content, metadata=metadata, topk=50, embeddings=embeddings)


@entry.delete('/knowledges/{knowledge_id}/{item_id}', status_code=204, tags=['Knowledge Base'])
@requires(['authenticated'])
async def delete_knowlege(knowledge_id: str, item_id: str, request: Request):
    await knowledge_base.delete(collection=knowledge_id, id=item_id)
