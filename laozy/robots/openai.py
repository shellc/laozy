from typing import Any, Optional, Coroutine
from uuid import UUID
from ..logging import log
from langchain.chat_models import ChatOpenAI

import openai
from langchain.chat_models import ChatOpenAI
from langchain import LLMChain
from langchain.callbacks.streaming_aiter import AsyncIteratorCallbackHandler
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

from ..message import Message

from .. import settings
from .base_robot import ChatRobot

openai_api_key = settings.get('OPENAI_API_KEY')
openai_api_base = settings.get('OPENAI_API_BASE')

llm = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0,
                 openai_api_key=openai_api_key, streaming=True)

openai.api_base = openai_api_base


class OpenAIRobot(ChatRobot):
    def __init__(self,
                 prompt_template: dict = {},
                 variables: list = [],
                 values: dict = {},
                 knowledge_base_id: str = None,
                 hisotry_limit: int = -1,
                 knowledge_limit: int = -1,
                 knowledge_query_limit: int = -1,
                 knowledge_max_length: int = -1
                 ) -> None:
        super().__init__(prompt_template,
                         variables,
                         values,
                         knowledge_base_id,
                         hisotry_limit,
                         knowledge_limit,
                         knowledge_query_limit,
                         knowledge_max_length)

    async def generate(self, msg: Message):
        history_limit = 4 if self.history_limit < 0 or self.history_limit > 20 else self.history_limit
        memory = await self.load_memory(current_msg=msg, limit=history_limit)

        chain = LLMChain(llm=llm, memory=memory,
                         prompt=self.prompt, verbose=False)

        varialbe_values = self.varialbe_values.copy()
        varialbe_values['prompt'] = msg.content

        knowledge_query_limit = 1 if self.knowledge_query_limit < 0 or self.knowledge_query_limit > 20 else self.knowledge_query_limit
        knowledge_query = self.plain_memory(memory=memory, limit=knowledge_query_limit) + '\n' + msg.content
        
        knowledge_limit = 10 if self.knowledge_limit < 0 or self.knowledge_limit > 10 else self.knowledge_limit
        knowledge_max_len = 1000 if self.knowledge_max_length < 0 or self.knowledge_max_length > 1000 else self.knowledge_max_length
        knowledge_ctx = await self.load_knowledges(query_text=knowledge_query, limit=knowledge_limit, max_length=knowledge_max_len)
        varialbe_values.update(knowledge_ctx)

        # log.info([self.prompt, varialbe_values])

        callbacks = []
        if msg.streaming:
            handler = AsyncIteratorCallbackHandler()
            msg.streaming_iter = handler.aiter()
            callbacks.append(handler)
            msg.event.set()

        return await chain.apredict(callbacks=callbacks, **varialbe_values)
