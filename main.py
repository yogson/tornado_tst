import tornado.ioloop
from tornado.web import Application

from config import ENDPOINTS


def make_app():
    return Application(ENDPOINTS)


if __name__ == "__main__":
    app = make_app()
    server = tornado.httpserver.HTTPServer(app)
    server.bind(8888)
    server.start(12)
    tornado.ioloop.IOLoop.current().start()
