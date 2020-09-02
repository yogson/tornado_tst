from tornado.web import RequestHandler, addslash


class MirrorHandler(RequestHandler):

    URI = r'/mirror/(.*)'

    @addslash
    def get(self, image=None):
        if image:
            self.write(image[:-1])
        else:
            print('A vampire!!!')
            self.write('You shell not pass!!!')
