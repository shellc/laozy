from ..message import Message


class Robot():
    def __init__(self, prompt_template: dict = {}, variables: list = [], values: dict = {}, knowledge_base_id: str = None) -> None:
        self.prompt_template = prompt_template
        self.variables = variables
        self.values = values
        self.knowledge_base_id = knowledge_base_id

    async def generate(msg: Message):
        pass
