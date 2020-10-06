from abc import ABC
import random

from tornado.web import RequestHandler

from cache import c


class LolHandler(RequestHandler, ABC):

    URI = r'/lol'

    def get(self):
        self.write('ROFL!!!\n')


class RandHandler(RequestHandler, ABC):

    URI = r'/random'

    def get(self):
        self.write(str(random.randint(1, 65564)))


class CacheHandler(RequestHandler, ABC):

    URI = r'/cached'

    def get(self):
        self.write(c.get('mirror', 'access_time'))