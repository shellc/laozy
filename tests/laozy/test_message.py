import asyncio
import aiounittest

from laozy.message import message


class TestMemoryMessageQueue(aiounittest.AsyncTestCase):
    def setUp(self) -> None:
        return super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()

    def create_message(self):
        return message.Message(id='msgid', connector='wxkf', connector_id='wxkf_id', connector_userid='user_id')

    async def test_put_get(self):
        q = message.MessageQueueInMemory()
        msg = self.create_message()

        await q.put(msg)

        r_msg = await q.get()

        self.assertEqual(r_msg.id, msg.id)

    async def test_consume(self):
        q = message.MessageQueueInMemory()
        qr = message.MessageQueueInMemory()

        async def consume(msg):
            if '9' == msg.id:
                await qr.put(msg)
            else:
                # raise Exception("Received message: %s" % msg.id)
                pass

        t = q.consume(consume)

        for i in range(10):
            msg = self.create_message()
            msg.id = str(i)
            await q.put(msg)

        msg = await qr.get()
        self.assertEqual('9', msg.id)
        t.cancel()
