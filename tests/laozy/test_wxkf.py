import aiounittest

from laozy import settings
from laozy.connectors.wx import wxkf_connector

def create_wxkf():
    wxkf_token = settings.get('WXKF_TOKEN', '')
    wxkf_encoding_aes_key = settings.get('WXKF_ENCODING_AES_KEY', '')
    wxkf_company_id = settings.get('WXKF_COMPANY_ID', '')
    wxkf_secret = settings.get('WXKF_SECRET', '')
    wxkf_service = wxkf_connector.WXKFConnector(
        wxkf_token, wxkf_encoding_aes_key, wxkf_company_id, wxkf_secret)
    
    return wxkf_service

class TestWxkf(aiounittest.AsyncTestCase):
    async def test_verify(self):
        s = create_wxkf()
        await s.verify("b18b010223992b1a43284c08a891ba663d68694e", 1683603499, 1683518676, "PS15I34dRNmIfcnqLUfy7DuvdimaSVH7TQuu+JC80TnILJdF8qn41bXkVISoATJBdU/2O2FQ3/6X2TK8ZJtRIw==")

    async def test_notify(self):
        s = create_wxkf()
        data = b'<xml><ToUserName><![CDATA[ww262759fa37c0a465]]></ToUserName><Encrypt><![CDATA[IWTJ3LmQdT5xb/18ow7YERAC/ke47/KhlAEK0eRjLEdhSaavJf8smDiaWAAGKo5pXi60Lt+sU+r1OCL319wZiIIBTi9vsX64Vb18K0iVQhgvWU+UYocaODvYH43hhljbGY0H/sIUO/rN6FF/zSD4T/eyVPl5ycomIIMP5R4/w/7KtGJej1dXgxLLXpdB7J9wwrlZqwpQC5RFS4DNs9fy8eIDqsI94u6e9AwfHBdm90t03yqiLz9rQWsHxbmuGhxI23XZ0qY1GkUBqsGoV1zv4DPiO+FN5NxykBv7MCAJBWUrXR8CVAQ7tcWCCNsc0sutLrVxZ17cWBEbmnI7Xvi+oesCQSyYO3px8EZoKcqBSH0lrppeeHGnqRhkf3NpgCm2/44unINuelu1L7ZXyRl2g/kE5TW/OjC54qCzrp/3HVmCVWIMb9EsD83mhyhvkX1wqtDcd7hzFYS+Y2XU+ZJab3gtlLno80X9LxpRGQPNXcjADoUy4nUAtiwGqlS6qMHF]]></Encrypt><AgentID><![CDATA[]]></AgentID></xml>'
        await s.notify("3f21ca9530d2adb8f78e7415b865eac0a5950d35", 1683612033, 1683810066, data)
        event = await s.events.get()
        kfid = event['kfid']
        token = event['token']
        
        self.assertEqual(token, "ENC4SudKmUeFBby4Ng6FEmWEaBVCSCjTC7RtgYiM5ZuZrcx")
        self.assertEqual(kfid, "wkQSyjJwAAJbbH9rcGLtuMX9ptEKBAfw")

    async def test_get_access_token(self):
        s = create_wxkf()
        await s.get_access_token()
        #print("token: %s, expires_in: %d" % (s.access_token, s.access_token_expires))
        self.assertIsNotNone(s.access_token)
        self.assertIsNotNone(s.access_token_expires)