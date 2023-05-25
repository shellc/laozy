import json
from ..message import Message

from langchain.memory import ConversationBufferMemory
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    AIMessagePromptTemplate,
    MessagesPlaceholder
)

from ..db import messages

from ..logging import log

from ..knowledge import knowledge_base, embeddings


class Robot():
    def __init__(self,
                 prompt_template: dict = None,
                 variables: list = None,
                 values: dict = None,
                 knowledge_base_id: str = None,
                 hisotry_limit: int = -1,
                 knowledge_limit: int = -1,
                 knowledge_query_limit: int = -1,
                 knowledge_max_length: int = -1) -> None:
        self.prompt_template = prompt_template
        self.variables = variables
        self.values = values
        self.knowledge_base_id = knowledge_base_id
        self.history_limit = hisotry_limit
        self.knowledge_limit = knowledge_limit
        self.knowledge_query_limit = knowledge_query_limit
        self.knowledge_max_length = knowledge_max_length

    async def generate(msg: Message):
        pass

    async def load_memory(self, limit=4):
        pass

    async def load_knowledges(self, limit=3):
        pass

    def plain_memory(self, memory, limit=1):
        messages = []
        if memory and memory.chat_memory:
            for m in memory.chat_memory.messages:
                messages.append(m.content)
        return '\n'.join(messages[-1*limit:])


class ChatRobot(Robot):
    def __init__(self,
                 prompt_template: dict = None,
                 variables: list = None,
                 values: dict = None,
                 knowledge_base_id: str = None,
                 hisotry_limit: int = -1,
                 knowledge_limit: int = -1,
                 knowledge_query_limit: int = -1,
                 knowledge_max_length: int = -1) -> None:
        super().__init__(prompt_template,
                         variables,
                         values,
                         knowledge_base_id,
                         hisotry_limit,
                         knowledge_limit,
                         knowledge_query_limit,
                         knowledge_max_length)

        self.history_enabled = False
        self.knowledge_enabled = False

        prompts = []

        if prompt_template:
            for t in prompt_template.get("prompts"):
                role = t['role']
                if 'system' == role and t['template']:
                    prompts.append(
                        SystemMessagePromptTemplate.from_template(t['template']))
                elif 'history' == role:
                    if 'template' in t and len(t['template']) > 0:
                        prompts.append(
                            SystemMessagePromptTemplate.from_template(t['template']))

                    variable_name = t['name'] if 'name' in t else 'history'
                    prompts.append(MessagesPlaceholder(
                        variable_name=variable_name))

                    self.history_enabled = True
                elif 'knowledge' == role and knowledge_base_id:
                    knowledge_prompt = ''
                    if 'template' in t and len(t['template']) > 0:
                        knowledge_prompt = t['template']

                    prompts.append(
                        SystemMessagePromptTemplate.from_template("%s\n {laozy_knowledges}" % knowledge_prompt))
                    self.knowledge_enabled = True
                else:
                    log.warn("Unknow role in prompt template: %s" % t['role'])

        prompts.append(HumanMessagePromptTemplate.from_template("{prompt}"))
        prompts.append(AIMessagePromptTemplate.from_template(""))

        self.prompt = ChatPromptTemplate.from_messages(prompts)

        self.varialbe_values = values

    async def load_memory(self, current_msg: Message, limit=4):
        memory = None

        if self.history_enabled:
            memory = ConversationBufferMemory(
                return_messages=True, input_key='prompt')

            if current_msg is not None:
                histories = await messages.get_history(
                    current_msg.connector,
                    current_msg.connector_id,
                    current_msg.connector_userid,
                    current_msg.channel_id,
                    last=limit
                )
                for h in reversed(histories):
                    if not h.content:
                        continue
                    if h.direction == 0:
                        memory.chat_memory.add_user_message(h.content)
                    else:
                        memory.chat_memory.add_ai_message(h.content)

        return memory

    async def load_knowledges(self, query_text: str, limit=3, max_length=1000):
        context = {}
        if self.knowledge_enabled:
            ks = await knowledge_base.retrieve(
                collection=self.knowledge_base_id,
                content=query_text,
                topk=limit,
                embeddings=embeddings
            )
            contents = []
            for k in ks:
                contents.append(k.content.replace('\n', ' '))

            ctx_str = ' '.join(contents)
            context = {'laozy_knowledges': ctx_str[:max_length]}

            # log.info('QUERY: %s, CONTEXT: %s' % (query_text.replace('\n', ' '), ctx_str[:50]))
        return context
