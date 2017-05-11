# coding:utf-8

import json
from datetime import datetime

import asyncio
import aiohttp_jinja2
from aiohttp import web


class LoginView(web.View):

    @aiohttp_jinja2.template('login.html')
    async def get(self):
        if self.request.cookies.get('user'):
            return web.HTTPFound('/')
        return {'title': 'Authentication'}

    async def post(self):
        response = web.HTTPFound('/')
        data = await self.request.post()
        response.set_cookie('user', data['name'])
        return response


async def logout_handler(request):
    response = web.HTTPFound('/')
    response.del_cookie('user')
    return response


@aiohttp_jinja2.template('index.html')
async def index_handler(request):
    r = request.app['redis']
    return {}
