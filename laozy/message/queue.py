from ..logging import log
from asyncio import Queue, ensure_future
from typing import Callable

from .message import Message

class MessageQueue():
    def __init__(self) -> None:
        pass

    async def put(self, msg: Message):
        pass

    async def get(self):
        pass

    def process(self, func: Callable):
        pass


class MessageQueueInMemory(MessageQueue):

    def __init__(self) -> None:
        super().__init__()
        self.q = Queue()

    async def put(self, msg: Message):
        self.q.put_nowait(msg)

    async def get(self):
        return await self.q.get()

    def process(self, callable: Callable):
        async def _consume():
            while True:
                msg = await self.q.get()
                try:
                    #await callable(msg)
                    ensure_future(callable(msg))
                except BaseException as e:
                    log.error("Process message faild!", exc_info=e)
                    
        return ensure_future(_consume())

    async def join(self):
        await self.q.join()
