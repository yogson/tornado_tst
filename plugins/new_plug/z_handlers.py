from tornado.web import RequestHandler, addslash

from base_handler import BaseHandler



class MirrorHandler(BaseHandler):

    URI = r'/mirror/(.*)'

    @addslash
    def get(self, image=None):
        if image:
            self.write(image[:-1])
        else:
            print('A vampire!!!')
            self.write('You shell not pass!!!')


class TestHandler(BaseHandler):

    URI = r'/test'

    def post(self):
        self.write('OK')
