from ..logging import log
from langchain.chat_models import ChatOpenAI

import openai
from langchain.chat_models import ChatOpenAI
from langchain import LLMChain
from langchain.callbacks.streaming_aiter import AsyncIteratorCallbackHandler

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
                 knowledge_base_id: str = None
                 ) -> None:
        super().__init__(prompt_template, variables, values, knowledge_base_id)

    async def generate(self, msg: Message):
        memory = await self.load_memory(current_msg=msg, limit=5)

        chain = LLMChain(llm=llm, memory=memory, prompt=self.prompt)

        varialbe_values = self.varialbe_values.copy()
        varialbe_values['prompt'] = msg.content

        knowledge_query = self.plain_memory(memory=memory)
        knowledge_ctx = await self.load_knowledges(query_text=knowledge_query, limit=2, max_length=2000)
        varialbe_values.update(knowledge_ctx)

        callbacks = []
        if msg.streaming:
            handler = AsyncIteratorCallbackHandler()
            msg.streaming_iter = handler.aiter()
            callbacks.append(handler)
            msg.event.set()

        return await chain.apredict(callbacks=callbacks, **varialbe_values)
