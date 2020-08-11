from abc import ABC
import random

from tornado.web import RequestHandler


class LolHandler(RequestHandler, ABC):

    URI = r'/lol'

    def get(self):
        self.write('ROFL!!!\n')


class RandHandler(RequestHandler, ABC):

    URI = r'/random'

    def get(self):
        self.write(str(random.randint(1, 65564)))