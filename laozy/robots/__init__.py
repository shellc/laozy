import json
import logging


from .. import db
from .openai import OpenAIRobot


log = logging.getLogger()


async def get_robot(id: str):
    robot = None
    r = await db.robots.get(id)
    prompt_template = {}
    variables = []
    values = {}
    knowledge_base_id = r.knowledge_base_id

    if r:
        if r.prompt_template_id:
            t = await db.prompt_templates.get(r.prompt_template_id)
            prompt_template = json.loads(t.template)
            variables = json.loads(t.variables)

        if r.variables:
            values = json.loads(r.variables)

        impl = r.implement
        if 'openai' == impl:
            robot = OpenAIRobot(
                prompt_template,
                variables,
                values,
                knowledge_base_id,
                r.history_limit,
                r.knowledge_limit,
                r.knowledge_query_limit,
                r.knowledge_max_length
            )
        else:
            log.error("Robot not implemented: %s" % impl)
    return robot
