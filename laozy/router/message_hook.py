import json
import aiohttp
from ..message import Message

from ..logging import log


async def post_message(url, msg: Message):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url,
                                    headers={
                                        'Content-Type': 'application/json'
                                    },
                                    data=json.dumps(msg.dict()),
                                    timeout=aiohttp.ClientTimeout(total=30)
                                    ) as r:
                status = r.status
                if status >= 200 and status <= 299:
                    reply = await r.json()
                    if 'content' in reply and reply['content']:
                        msg.content = reply['content']
                    if 'extra' in reply and reply['extra']:
                        msg.extra = reply['extra']
                else:
                    log.warning(
                        'Message hook error: URL=%s, error=%s', (url, status))
    except Exception as e:
        log.warning('Message hook error: URL=%s, error=%s', (url, e))
    return msg
