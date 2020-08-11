import tornado.ioloop
from tornado.web import Application

from config import ENDPOINTS


def make_app():
    return Application(ENDPOINTS)


if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
