import json

from tornado.web import RequestHandler

from role_model import Auth


class BaseHandler(RequestHandler):

    def initialize(self):
        self.data = None

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Origin', 'http://127.0.0.1:9090')

    def prepare(self):
        self.data = json.loads(self.request.body) if self.request.body else dict()

    def not_implemented(self):
        self._reason = 'Method not implemented'
        self.send_error(405)

    def get(self):
        self.not_implemented()

    def post(self):
        self.not_implemented()

    @Auth()
    def put(self):
        self.not_implemented()

    def delete(self):
        self.not_implemented()


    @Auth(is_handler=False, permission='do_smth')
    def do_smth(*args):
        print('I have the right!')