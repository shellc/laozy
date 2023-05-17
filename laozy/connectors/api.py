import logging
import asyncio
import json
from typing import Union
from pydantic import BaseModel
from fastapi import Request, HTTPException, status
from fastapi.responses import Response, StreamingResponse
from starlette.authentication import requires

from ..db import channel_routes, messages
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
    content: str


@entry.get('/connectors/messages')
@requires('authenticated')
async def get_messages(connector_id: str, request: Request):
    userid = request.user.userid
    route = await channel_routes.get_route('web', connector_id)
    if not route:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    histories = await messages.get_history('web', connector_id, userid, route.channel_id, 20)
    return histories


@entry.post('/connectors/messages')
@requires('authenticated')
async def new_message(wmsg: WebMessage, sse: bool = False, request: Request = None):
    userid = request.user.userid
    msg = Message(connector_id=wmsg.connector_id,
                  content=wmsg.content, connector_userid=userid)

    log.info("Received message: %s" % msg.id)
    msg.streaming = True
    msg.event = asyncio.Event()

    await web_connector.receive(msg)
    await msg.event.wait()

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
        elif msg.msgtype == 'error':  # error occurred
            yield "event: error\ndata: %s\n\n" % json.dumps({"e": msg.content})

    content_type = 'text/event-stream' if sse else 'text/plain'
    return StreamingResponse(aiter(), headers={'Content-Type': content_type})


# WeChat Customer Service APIs

__wxkf_token = settings.get('WXKF_TOKEN', '')
__wxkf_encoding_aes_key = settings.get('WXKF_ENCODING_AES_KEY', '')
__wxkf_compay_id = settings.get('WXKF_COMPANY_ID', '')
__wxkf_secret = settings.get('WXKF_SECRET', '')

wxkf_connector = WXKFConnector(
    __wxkf_token, __wxkf_encoding_aes_key, __wxkf_compay_id, __wxkf_secret)

__buildin_connectors['wxkf'] = wxkf_connector


@entry.get('/connectors/wxkf/notifications')
async def wxkf_verify(msg_signature: str, timestamp: int, nonce: int, echostr: str, request: Request):
    """
    Provide a callback URL for WeChat customer service to verify our service.
    """

    reply_echostr = await wxkf_connector.verify(
        msg_signature, timestamp, nonce, echostr)
    if reply_echostr is None:
        raise HTTPException(status_code=400, detail='Verify signature failed.')
    else:
        return Response(content=reply_echostr)


@entry.post('/connectors/wxkf/notifications')
async def wxkf_notify(msg_signature: str, timestamp: int, nonce: int, request: Request):
    """
    Provide a callback URL to receive notifications from WeChat customer service.
    """
    data = await request.body()
    await wxkf_connector.notify(msg_signature, timestamp, nonce, data)
