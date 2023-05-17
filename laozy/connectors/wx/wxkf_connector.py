import time
import json
import uuid
from typing import Awaitable

from asyncio import Queue, ensure_future
import aiohttp
import xml.etree.cElementTree as ET

from laozy.message import Message

from ...logging import log
from . import WXBizMsgCrypt3
from ... import db
from ..base_connector import Connector


class WXKFConnector(Connector):
    """
    WeChat Cusomter Service

    API Document: https://kf.weixin.qq.com/api/doc/
    """
    gettoken_endpint = "https://qyapi.weixin.qq.com/cgi-bin/gettoken"
    endpint = "https://qyapi.weixin.qq.com/cgi-bin/kf/"

    def __init__(self, token: str, key: str, company_id: str, secret: str) -> None:
        super().__init__()

        self.company_id = company_id
        self.secret = secret
        self.access_token = None
        self.access_token_expires = 0

        self.wxmsg_crypt = WXBizMsgCrypt3.WXBizMsgCrypt(token, key, company_id)
        self.events = Queue()

        self.next_cursor = None

    async def verify(self, msg_signature: str, timestamp: int, nonce: int, echostr: str):
        """
        Generate a string for verification and send it back to WeChat customer service.
        """

        status, reply_echostr = self.wxmsg_crypt.VerifyURL(
            msg_signature, timestamp, nonce, echostr)

        return reply_echostr if status == 0 else None

    def __parse_event_msg(self, content):
        """
        Parse event message received from WeChat Customer Service.
        """
        try:
            xml = ET.fromstring(content)
            msg_type = xml.find("MsgType").text
            if msg_type == 'event':
                event = xml.find('Event').text
                if event == 'kf_msg_or_event':
                    token = xml.find('Token').text
                    kfid = xml.find('OpenKfId').text
                    return token, kfid
                else:
                    log.error("Unkonw event: %s" % event)
            else:
                log.error("Unkonw message type: %s" % msg_type)
        except Exception as e:
            log.error(e, exc_info=e)
        return None, None

    async def notify(self, msg_signature: str, timestamp: int, nonce: int, data: bytes):
        """
        Handle notification events received from WeChat customer service.
        """
        status, content = self.wxmsg_crypt.DecryptMsg(
            data.decode('utf-8'), msg_signature, timestamp, nonce)

        if status != 0:
            log.error("Receive notification error: %d" % status)
        else:
            token, kfid = self.__parse_event_msg(content)
            await self.events.put({"kfid": kfid, "token": token})

    async def get_access_token(self, refresh: bool = False):
        if int(time.time()) < self.access_token_expires and not refresh:
            return

        url = "%s?corpid=%s&corpsecret=%s" % (
            self.gettoken_endpint, self.company_id, self.secret)

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                status = response.status
                if status != 200:
                    log.error("Get access token error: %d" % status)
                else:
                    r = await response.json()
                    errcode = r['errcode']
                    if errcode != 0:
                        log.error("Get access token error: errcode=%d, errmsg=%s" % (
                            errcode, r['errmsg']))
                    else:
                        self.access_token = r['access_token']
                        self.access_token_expires = r['expires_in'] + \
                            int(time.time()) - 300
        return self.access_token, self.access_token_expires

    def __auto_refresh_token(func):
        async def wrapper(*args, **kwargs):
            self = args[0]
            await self.get_access_token()
            status = await func(*args, **kwargs)
            if status == 40014:  # Invalid token
                await self.get_access_token(refresh=True)
                status = await func(*args, **kwargs)
            return status
        return wrapper

    def __transform_message(self, msg):
        msgid = msg['msgid']
        send_time = msg['send_time']
        # orgin = msg['origin']
        msgtype = msg['msgtype']

        if 'event' == msgtype:
            log.info("The message type is `event`, it will be ignored.")
            return

        kfid = msg['open_kfid']
        external_userid = msg['external_userid']

        content = None

        if 'text' == msgtype:
            content = msg['text']['content']
        elif 'image' == msgtype:
            content = msg['image']['media_id']
        elif 'voice' == msgtype:
            content = msg['voice']['media_id']
        elif 'video' == msgtype:
            content = msg['video']['media_id']
        elif 'file' == msgtype:
            content = msg['file']['media_id']
        elif 'location' == msgtype:
            content = json.dumps(msg['location'])
        else:
            log.error("Unsupported message type: %s" % msgtype)
            return

        return Message(id=uuid.uuid1().hex, connector='wxkf', connector_id=kfid, connector_userid=external_userid,
                       connector_msgid=msgid, send_time=send_time, msgtype=msgtype, content=content)

    @__auto_refresh_token
    async def sync_msg(self, kfid: str, token: str, limit: int = 1000, voice_format: int = 0):
        retcode = 0

        url = "%s/sync_msg?access_token=%s" % (self.endpint, self.access_token)

        data = {
            "open_kfid": kfid,
            "token": token,
            "limit": limit,
            "voice_format": voice_format
        }
        if self.next_cursor:
            data["cursor"] = self.next_cursor

        request_body = json.dumps(data)

        has_more = 0
        next_cursor = None
        msg_list = []

        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=request_body) as response:
                status = response.status
                if status != 200:
                    log.error("Sync message error: %d" % status)
                    retcode = status
                else:
                    r = await response.json()
                    errcode = r['errcode']
                    if errcode != 0:
                        log.error("Sync message error: errcode=%d, errmsg=%s" % (
                            errcode, r['errmsg']))
                        retcode = errcode
                    else:
                        has_more = r['has_more']
                        next_cursor = r['next_cursor']
                        msg_list = r['msg_list']

        if retcode == 0:
            if self.received is not None:
                for msg in msg_list:
                    try:
                        message = self.__transform_message(msg)
                        if message is not None:
                            await self.received.put(message)
                    except Exception as e:
                        log.error("Handle message error: %s" %
                                  str(e), exc_info=e)
            else:
                log.warn(
                    "The message queue was not found, so the message will be printed on the console.")
                log.info(msg_list)

            if next_cursor is not None:
                self.next_cursor = next_cursor

            if has_more == 1:
                retcode = await self.sync_msg(kfid=kfid, token=token, limit=limit, voice_format=voice_format)

        return retcode

    def start(self, awaitable: Awaitable = None):
        super().start(awaitable=awaitable)

        async def _process():
            while True:
                event = await self.events.get()
                try:
                    kfid = event['kfid']
                    token = event['token']

                    # load next_cursor
                    self.next_cursor = await db.states.get_state('wxkf_next_cursor')

                    errcode = await self.sync_msg(kfid=kfid, token=token)

                    # save next_cursor
                    log.info("Save wxkf_next_cursor=%s" % self.next_cursor)
                    await db.states.set_state('wxkf_next_cursor', self.next_cursor)

                    if errcode != 0:
                        log.error("Sync message error: %d" % errcode)
                except BaseException as e:
                    log.error(e, exc_info=e)
                finally:
                    self.events.task_done()
        return ensure_future(_process())

    @__auto_refresh_token
    async def send_msg(self, msg: Message):
        retcode = 0

        url = "%s/send_msg?access_token=%s" % (self.endpint, self.access_token)

        data = {
            "touser": msg.connector_userid,
            "open_kfid": msg.connector_id,
            "msgid": msg.id,
            "msgtype": "text",
            "text": {
                "content": msg.content
            }
        }
        request_body = json.dumps(data)

        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=request_body) as response:
                status = response.status
                if status != 200:
                    log.error("Send message error: %d" % status)
                    retcode = status
                else:
                    r = await response.json()
                    errcode = r['errcode']
                    if errcode != 0:
                        log.error("Send message error: errcode=%d, errmsg=%s" % (
                            errcode, r['errmsg']))
                        retcode = errcode
        return retcode

    async def onsend(self, msg: Message):
        await self.send_msg(msg)
