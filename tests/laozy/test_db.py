import asyncio
from collections.abc import Callable
from typing import Any
import aiounittest

from laozy.db import db
from laozy.message import message


class TestModels(aiounittest.AsyncTestCase):
    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    async def test_create_message(self):
        await db.instance.clear_messages()

        msg = message.Message(id='msg_id_test_create_message', connector='wxkf', connector_id='wxkf_id', connector_userid='wx_user_id', robot_id='assistant_id')
        
        await db.instance.save_message(**msg.__dict__)

        msg_r = await db.instance.get_messages(origin='wxkf', origin_id='wxkf_id', origin_user_id='wx_user_id', assistant_id='assistant_id')
        self.assertEqual(msg.id, msg_r[0].id)

    async def test_stat(self):
        await db.instance.set_state('wxkf_next_cursor', 'xxx')
        wxkf_next_cursor = await db.instance.get_state('wxkf_next_cursor')
        self.assertEqual('xxx', wxkf_next_cursor)