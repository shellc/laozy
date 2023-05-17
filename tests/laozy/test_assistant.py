import aiounittest
from laozy.db import db
from laozy.robots import openai
from laozy.message import message

class TestAssistant(aiounittest.AsyncTestCase):

    async def test_chat(self):
        #msg = message.Message(id='id', origin='origin', origin_id='origin_id', origin_user_id='userid', content='hi')
        
        r = await openai.xiaoxin.generate(None, assistant_name='小芯', doctor_name='罗医生', text="你好,请罗医生回答")
        print(r)
