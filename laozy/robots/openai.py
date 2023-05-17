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
    MessagesPlaceholder
)

from ..db import messages
from ..message import Message

from .. import connectors
from .. import settings
from .base_robot import Robot

openai_api_key = settings.get('OPENAI_API_KEY')
openai_api_base = settings.get('OPENAI_API_BASE')

llm = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0,
                 openai_api_key=openai_api_key, streaming=True)

openai.api_base = openai_api_base


class OpenAIRobot(Robot):
    def __init__(self, prompt_template: dict = ..., variables: list = ..., values: dict = ...) -> None:
        super().__init__(prompt_template, variables, values)

        prompts = []
        if prompt_template:
            for t in prompt_template.get("prompts"):
                role = t['role']
                if 'system' == role and t['template']:
                    prompts.append(
                        SystemMessagePromptTemplate.from_template(t['template']))
                elif 'history' == role:
                    variable_name = t['name'] if t['name'] else 'history'
                    prompts.append(MessagesPlaceholder(
                        variable_name=variable_name))
                else:
                    log.warn("Unknow role in prompt template: %s" % t['role'])

        prompts.append(HumanMessagePromptTemplate.from_template("{prompt}"))
        # history_placeholder = MessagesPlaceholder(variable_name="history")
        self.prompt = ChatPromptTemplate.from_messages(prompts)

        self.varialbe_values = values

    async def generate(self, msg: Message):
        memory = ConversationBufferMemory(
            return_messages=True, input_key='prompt')
        if msg is not None:
            histories = await messages.get_history(msg.connector, msg.connector_id, msg.connector_userid, msg.channel_id, 11)
            for h in reversed(histories):
                if not h.content:
                    continue
                if h.direction == 0:
                    memory.chat_memory.add_user_message(h.content)
                else:
                    memory.chat_memory.add_ai_message(h.content)

        chain = LLMChain(
            llm=llm, memory=memory, prompt=self.prompt, verbose=False)

        vvalues = self.varialbe_values.copy()
        vvalues['prompt'] = msg.content

        callbacks = []
        if msg.streaming:
            handler = AsyncIteratorCallbackHandler()
            msg.streaming_iter = handler.aiter()
            callbacks.append(handler)
            msg.event.set()

        return await chain.apredict(callbacks=callbacks, **vvalues)
