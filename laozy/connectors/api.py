import logging
import asyncio
import json
from typing import Optional, List
from pydantic import BaseModel
from fastapi import Request, HTTPException, status
from fastapi.responses import Response, StreamingResponse
from starlette.authentication import requires

from ..db import channel_routes, messages, MessagePdModel
from ..api import entry

from .wx import WXKFConnector
from .web_connector import WebConnector

from .. import settings
from ..message import queue, Message

log = logging.getLogger('Connectors')

__buildin_connectors = {}

# Web Connector
web_connector = WebConnector()
__buildin_connectors['web'] = web_connector


class WebMessage(BaseModel):
    connector_id: str
    connector_userid: Optional[str] = None
    content: str


@entry.get('/connectors/messages', tags=['Connector'])
@requires('authenticated')
async def get_history(connector_id: str, request: Request, connector_userid: Optional[str] = None, limit: Optional[int] = 20) -> List[MessagePdModel]:
    """
    Get conversation history from the connector.
    """

    if not connector_userid:
        connector_userid = request.user.userid

    if limit < 0 or limit > 100:
        limit = 20

    route = await channel_routes.get_route('web', connector_id)
    if not route:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    histories = await messages.get_history('web', connector_id, connector_userid, route.channel_id, limit)
    return histories


@entry.post('/connectors/messages', tags=['Connector'])
@requires('authenticated')
async def send_message(wmsg: WebMessage, request: Request, sse: bool = False):
    connector_userid = wmsg.connector_userid
    if not connector_userid:
        connector_userid = request.user.userid

    msg = Message(connector_id=wmsg.connector_id,
                  content=wmsg.content, connector_userid=connector_userid)

    log.info("Received message: %s" % msg.id)
    msg.streaming = True
    msg.event = asyncio.Event()

    await web_connector.receive(msg)
    await msg.event.wait()
    msg.event.clear()

    log.info("Generate for message: %s" % msg.id)

    # python 3.10 required
    async def aiter():
        if msg.streaming_iter:

            async for c in msg.streaming_iter:
                if sse:
                    e = {
                        "c": c
                    }
                    yield "event: message\ndata: %s\n\n" % json.dumps(e)
                else:
                    yield c
            
            await msg.event.wait() # waitting for end
            if msg.extra:
                yield "event: extra\ndata: %s\n\n" % json.dumps(msg.extra)

        elif msg.msgtype == 'error':  # error occurred
            yield "event: error\ndata: %s\n\n" % json.dumps({"e": msg.content})

    content_type = 'text/event-stream' if sse else 'text/plain'
    return StreamingResponse(aiter(), headers={'Content-Type': content_type})


# WeChat Customer Service APIs

wxkf_connector = None

wxkf_enabled = settings.get_bool('WXKF_ENABLED')
if wxkf_enabled:
    __wxkf_token = settings.get('WXKF_TOKEN', '')
    __wxkf_encoding_aes_key = settings.get('WXKF_ENCODING_AES_KEY', '')
    __wxkf_compay_id = settings.get('WXKF_COMPANY_ID', '')
    __wxkf_secret = settings.get('WXKF_SECRET', '')
    wxkf_connector = WXKFConnector(
        __wxkf_token, __wxkf_encoding_aes_key, __wxkf_compay_id, __wxkf_secret)

    __buildin_connectors['wxkf'] = wxkf_connector

def check_wxkf_enabled():
    if not wxkf_enabled:
        raise HTTPException(status_code=503, detail='WeChat Customer Service is not enabled.')

@entry.get('/connectors/wxkf/notifications', tags=['WeChat'])
async def service_verify(msg_signature: str, timestamp: int, nonce: int, echostr: str, request: Request):
    """
    Provide a callback URL for WeChat customer service to verify our service.
    """

    check_wxkf_enabled()

    reply_echostr = await wxkf_connector.verify(
        msg_signature, timestamp, nonce, echostr)
    if reply_echostr is None:
        raise HTTPException(status_code=400, detail='Verify signature failed.')
    else:
        return Response(content=reply_echostr)


@entry.post('/connectors/wxkf/notifications', tags=['WeChat'])
async def message_notify(msg_signature: str, timestamp: int, nonce: int, request: Request):
    check_wxkf_enabled()
    
    """
    Provide a callback URL to receive notifications from WeChat customer service.
    """
    data = await request.body()
    await wxkf_connector.notify(msg_signature, timestamp, nonce, data)
