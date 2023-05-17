import asyncio
import aiounittest

async def add(x, y):
    await asyncio.sleep(0.1)
    return x + y

class TestAdd(aiounittest.AsyncTestCase):
    async def test_add(self):
        r = await add(5, 6)
        self.assertEqual(r, 11)