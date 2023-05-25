from . import apps
from .logging import log
import contextlib

from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.authentication import requires
from starlette.staticfiles import StaticFiles
from starlette.responses import RedirectResponse

from . import settings
from . import api
from .message import queue
from . import db
from . import connectors
from . import router
from . import admin
from .users import auth
from . import template

# Setup message providers
received = queue.MessageQueueInMemory()
connectors.manager.received = received


@contextlib.asynccontextmanager
async def lifespan(app):
    await db.instance.connect()

    connectors.manager.start()

    # Setup robots
    await router.start()

    yield
    await db.instance.disconnect()

# Routes
routes = [
    Route(
        '/',
        name="home",
        endpoint=lambda _: RedirectResponse('/developer')
    ),
    Route(
        '/accounts/login',
        name="login",
        endpoint=template.render(
            'account.html',
            context={
                'invitation_required': settings.get('INVITATION_REQUIRED', False)
            }
        )
    ),
    Route(
        '/developer',
        name="developer",
        endpoint=requires(
            scopes=['developer'],
            redirect='login')(template.render('developer.html'))
    ),
    Mount(
        '/static',
        name='static',
        app=StaticFiles(directory='static')
    ),
    Mount(
        '/api',
        name='api',
        app=api.entry,
    ),
]

routes.extend(apps.routes)

# Middlewares
middleware = [
    Middleware(AuthenticationMiddleware, backend=auth.BasicAuthBackend())
]

entry = Starlette(debug=True, routes=routes,
                  middleware=middleware, lifespan=lifespan)

admin.enable_admin(entry)

log.info("Welcome to Laozy.")
