from starlette.requests import Request
from starlette.templating import Jinja2Templates

templates = Jinja2Templates(directory='templates')

def render(template_name, context = {}):
    async def _request(request):
        context['request'] = request
        return templates.TemplateResponse(template_name, context=context)
    return _request