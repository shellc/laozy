from ..message import Message


class Robot():
    def __init__(self, prompt_template: dict = {}, variables: list = [], values: dict = {}) -> None:
        self.prompt_template = prompt_template
        self.variables = variables
        self.values = values

    async def generate(msg: Message):
        pass
