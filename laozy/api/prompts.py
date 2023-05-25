import time
import json
import re
from typing import List
from pydantic import BaseModel
from starlette.authentication import requires
from fastapi import Request, HTTPException

from .entry import entry
from ..db import prompt_templates, PromptTemplatesPdModel
from ..utils import uuid


@entry.get('/prompts/{id}', tags=['Prompt'])
@requires(['authenticated'])
async def get_prompt_template(id:str, request: Request) -> PromptTemplatesPdModel:
    return await prompt_templates.get(id)

@entry.get('/prompts', tags=['Prompt'])
@requires(['authenticated'])
async def list_prompt_templates(request: Request) -> List[PromptTemplatesPdModel]:
    return await prompt_templates.getbyowner(request.user.userid)


class PromptTemplateModel(BaseModel):
    name: str
    template: str


@entry.post('/prompts', status_code=201, tags=['Prompt'])
@requires(['authenticated'])
async def create_prompt_template(template: PromptTemplateModel, request: Request) -> PromptTemplatesPdModel:
    j = validate_template(template.template)
    variables = json.dumps(extract_variables(j), ensure_ascii=False)

    t = {
        'id': uuid(),
        'name': template.name,
        'template': template.template,
        'variables': variables,
        'owner': request.user.userid,
        'created_time': int(time.time())
    }
    await prompt_templates.create(**t)
    return PromptTemplatesPdModel(**t)


@entry.put('/prompts/{id}', status_code=200, tags=['Prompt'])
@requires(['authenticated'])
async def modify_prompt_template(id: str, template: PromptTemplateModel, request: Request) -> PromptTemplatesPdModel:
    j = validate_template(template.template)
    variables = json.dumps(extract_variables(j), ensure_ascii=False)

    await prompt_templates.update(id, variables=variables, **template.dict())
    r = {
        'id': id,
        'name': template.name,
        'template': template.template,
        'variables': variables
    }
    return PromptTemplatesPdModel(**r)


def validate_template(template: str):
    try:
        j = json.loads(template)
        if len(j) > 1:
            raise ValueError()
        if len(j) > 0 and 'prompts' not in j:
            raise ValueError()

        for p in j['prompts']:
            if len(p) > 0 and ('role' not in p or 'template' not in p):
                raise ValueError()
            if len(p) > 2:
                raise ValueError()
        return j
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid template format.")


__var_re = re.compile(r'{(.*?)}')


def extract_variables(template: str):
    if not template or 'prompts' not in template:
        return
    prompts = template['prompts']

    variables = set()
    for p in prompts:
        vars = __var_re.findall(p['template'])
        for v in vars:
            variables.add(v)
    return list(variables)

@entry.delete('/prompts/{id}', status_code=204, tags=['Prompt'])
@requires(['authenticated'])
async def remove_prompt_template(id:str, request: Request):
    await prompt_templates.delete(id)