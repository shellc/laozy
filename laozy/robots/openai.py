from ..logging import log
import asyncio
from langchain.chat_models import ChatOpenAI

import openai
from langchain.chat_models import ChatOpenAI
from langchain import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.callbacks.streaming_aiter import AsyncIteratorCallbackHandler

from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    AIMessagePromptTemplate,
    MessagesPlaceholder
)

from ..db import messages
from ..message import Message

from .. import connectors
from .. import settings
from .base_robot import Robot
from ..knowledge import knowledge_base

openai_api_key = settings.get('OPENAI_API_KEY')
openai_api_base = settings.get('OPENAI_API_BASE')

llm = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0,
                 openai_api_key=openai_api_key, streaming=True)

openai.api_base = openai_api_base


class OpenAIRobot(Robot):
    def __init__(self, prompt_template: dict = ..., variables: list = ..., values: dict = ..., knowledge_base_id: str = None) -> None:
        super().__init__(prompt_template, variables, values, knowledge_base_id)

        prompts = []

        if prompt_template:
            for t in prompt_template.get("prompts"):
                role = t['role']
                if 'system' == role and t['template']:
                    prompts.append(
                        SystemMessagePromptTemplate.from_template(t['template']))
                elif 'history' == role:
                    if 'template' in t and len(t['template']) > 0:
                        prompts.append(SystemMessagePromptTemplate.from_template(t['template']))

                    variable_name = t['name'] if 'name' in t else 'history'
                    prompts.append(MessagesPlaceholder(
                        variable_name=variable_name))
                else:
                    log.warn("Unknow role in prompt template: %s" % t['role'])
        
        if knowledge_base_id:
            prompts.append(SystemMessagePromptTemplate.from_template("{__laozy_context}"))

        prompts.append(HumanMessagePromptTemplate.from_template("{prompt}"))
        prompts.append(AIMessagePromptTemplate.from_template(""))
        # history_placeholder = MessagesPlaceholder(variable_name="history")
        self.prompt = ChatPromptTemplate.from_messages(prompts)

        self.varialbe_values = values

    async def generate(self, msg: Message):
        memory = ConversationBufferMemory(
            return_messages=True, input_key='prompt')
        if msg is not None:
            histories = await messages.get_history(msg.connector, msg.connector_id, msg.connector_userid, msg.channel_id, 3)
            for h in reversed(histories):
                if not h.content:
                    continue
                if h.direction == 0:
                    memory.chat_memory.add_user_message(h.content)
                else:
                    memory.chat_memory.add_ai_message(h.content)
        
        chain = LLMChain(
            llm=llm, memory=memory, prompt=self.prompt, verbose=True)

        vvalues = self.varialbe_values.copy()
        vvalues['prompt'] = msg.content

        if self.knowledge_base_id:
            ks = await knowledge_base.retrieve(collection=self.knowledge_base_id, content=msg.content)
            contents = []
            for k in ks:
                contents.append(k.content)
            vvalues['__laozy_context'] = "Context in triple quotes:'''%s'''\n" % '\n'.join(contents)
        
        callbacks = []
        if msg.streaming:
            handler = AsyncIteratorCallbackHandler()
            msg.streaming_iter = handler.aiter()
            callbacks.append(handler)
            msg.event.set()

        return await chain.apredict(callbacks=callbacks, **vvalues)
