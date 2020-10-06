from datetime import datetime

from tornado.web import RequestHandler, addslash

from base_handler import BaseHandler

from cache import c


class MirrorHandler(BaseHandler):

    URI = r'/mirror/(.*)'
    one_min_cache = c.new_realm('mirror')

    @addslash
    def get(self, image=None):
        self.one_min_cache['access_time'] = datetime.strftime(datetime.now(), '%d.%m.%Y %H:%M:%S')
        if image:
            self.write(image[:-1])
        else:
            print('A vampire!!!')
            self.write('You shell not pass!!!')


class TestHandler(BaseHandler):

    URI = r'/test'

    def get(self):
        self.write('OK')

    def post(self):
        self.write('OK')
