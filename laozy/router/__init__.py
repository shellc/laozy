from ..logging import log

from .. import connectors
from .message_processor import process


async def start():
    connectors.manager.received.process(process)
