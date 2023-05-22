from starlette.routing import Route

from . import wpa

routes = [
    Route('/apps/{connector_id}', wpa.generate_render('wpa.html')),
    Route('/apps/{connector_id}/manifest.webmanifest', wpa.generate_render('wpa.webmanifest', headers={'Content-Type': 'application/json'})),
    Route('/apps/{connector_id}/sw.js', wpa.generate_render('wpa_sw.js', headers={'Content-Type': 'text/javascript'})),
]