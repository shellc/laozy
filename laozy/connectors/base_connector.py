from ..logging import log
import asyncio
from typing import Awaitable
from ..message import Message, MessageQueue, MessageQueueInMemory


class Connector():
    def __init__(self) -> None:

        # Messages Received Queue
        self.__received = MessageQueueInMemory()
        self.__send = MessageQueueInMemory()

    @property
    def received(self) -> MessageQueue:
        return self.__received

    @received.setter
    def received(self, received: MessageQueue):
        self.__received = received

    async def send(self, msg: Message):
        await self.__send.put(msg)

    async def onsend(self, msg: Message):
        pass

    def start(self, awaitable: Awaitable = None) -> asyncio.Task:
        self.__send.process(self.onsend)
        if awaitable:
            return asyncio.ensure_future(awaitable)
