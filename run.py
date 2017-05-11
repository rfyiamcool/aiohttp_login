import logging
import asyncio
import aiohttp_jinja2
import aiohttp_debugtoolbar
import aioredis
import jinja2
from aiohttp import web, log
from collections import defaultdict
from aiohttp_debugtoolbar import toolbar_middleware_factory

import handlers


async def static_processor(request):
    return {'STATIC_URL': '/static/'}

async def auth_processor(request):
    return {'current_user': request.cookies.get('user')}


async def auth_cookie_factory(app, handler):
    async def auth_cookie_handler(request):
        if request.path != '/login' and request.cookies.get('user') is None:
            # redirect
            return web.HTTPFound('/login')
        return await handler(request)
    return auth_cookie_handler


async def get_app(debug=False):

    # Graceful shutdown actions

    async def close_redis(app):
        keys = await app['redis'].keys('channels*:users')

        # await app['redis'].delete(*keys)
        for key in keys:
            await app['redis'].delete(key)
        log.server_logger.info('Closing redis')
        app['redis'].close()


    middlewares = [auth_cookie_factory]

    if debug:
        middlewares += [toolbar_middleware_factory]

    app = web.Application(middlewares=middlewares)

    if debug:
        aiohttp_debugtoolbar.setup(app, intercept_redirects=False)
    router = app.router
    router.add_route('GET', '/', handlers.index_handler)
    router.add_route('*', '/login', handlers.LoginView)
    router.add_route('GET', '/logout', handlers.logout_handler)
    router.add_static('/static', 'static')

    aiohttp_jinja2.setup(app,
                         loader=jinja2.FileSystemLoader('templates/core'),
                         context_processors=[static_processor, auth_processor])

    app['redis'] = await aioredis.create_redis(('localhost', 6379),
                                               db=1, encoding='utf-8')
    app.on_shutdown.append(close_redis)

    return app

if __name__ == '__main__':
    debug = True
    if debug:
        logging.basicConfig(level='DEBUG')
    loop = asyncio.get_event_loop()
    app = loop.run_until_complete(get_app(debug))
    web.run_app(app)
