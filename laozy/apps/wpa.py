from starlette.responses import Response
from ..template import templates

from ..db import channel_routes

def generate_render(template, headers=None):
    async def _render(request):
        ctx = {'request': request}
        connector_id = request.path_params['connector_id']

        route = await channel_routes.get_route('web', connector_id)
        if not route:
            return Response(status_code=404)
        
        app = {
            'id': route.connector_id,
            'name': route.name,
        }
        
        ctx['app'] = app
        return templates.TemplateResponse(template, context=ctx, headers=headers)
    
    return _render