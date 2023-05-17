from ..logging import log
from ..message import Message, MessageQueue
from .api import __buildin_connectors


class ConnectorMananger:
    def __init__(self, connectors) -> None:
        self.__received = None
        self.connectors = connectors

    @property
    def received(self):
        return self.__received

    @received.setter
    def received(self, received: MessageQueue):
        self.__received = received

        for c in self.connectors.values():
            c.received = self.received

    async def send(self, msg: Message):
        connector = self.connectors.get(msg.connector)
        if connector:
            await connector.send(msg)
        else:
            log.error("Send message to %s is not supported." % msg.connector)

    def start(self):
        for c in self.connectors.values():
            c.start()


manager = ConnectorMananger(__buildin_connectors)
