from random import randint

import jwt
import asyncio


class _UserAuthChecker:

    SECRET_KEY = 'zxcnoidwa34rwv4etr3Q2GHVBTNYI5NU6R5EBASd2qSAZ'

    def __init__(self, request):
        self.request = request
        self._token = self._get_token()

    def _get_token(self):
        auth_header = self.request.headers.get('Authorization', None)

        if not auth_header:
            return

        auth_header_parts = auth_header.split()
        if auth_header_parts[0].lower() != 'bearer':
            return
        elif len(auth_header_parts) == 1:
            return
        elif len(auth_header_parts) > 2:
            return

        return auth_header_parts[1]

    @property
    def token(self):
        try:
            return self._decode_token(self._token)
        except (jwt.ExpiredSignatureError, jwt.DecodeError) as e:
            print(e)
            return

    @staticmethod
    def _decode_token(token):
        return jwt.decode(token, _UserAuthChecker.SECRET_KEY, algorithms='HS256')

    @staticmethod
    def _create_token(payload):
        return jwt.encode(payload, _UserAuthChecker.SECRET_KEY, algorithm='HS256')


class Auth(object):

    def __init__(self, is_handler=True, **kwargs):
        self.is_handler = is_handler
        self.permission = kwargs.get('permission')
        self.resource = kwargs.get('resource')

    def __call__(self, func):

        async def wrapped(*args):

            handler = args[0] if self.is_handler else None
            permission = self.permission or func.__name__
            resource = self.resource or handler.URI if handler else None

            token = _UserAuthChecker(handler.request).token

            if not token:
                return handler.send_error(401)

            user_id = token.get('sub')

            authorized = Authorizer().authorize(user_id, resource, permission)

            if authorized:
                return func(*args)
            else:
                return handler.send_error(403)

        return wrapped


class Authorizer:

    def __init__(self):
        self.subject = None
        self.object = None
        self.action = None

    def authorize(self, subj, obj, act):
        if subj and obj and act:
            self.subject = subj
            self.object = obj
            self.action = act
        else:
            raise ValueError

        if randint(0, 1):
            print(f'{self.subject} is authorized to {self.action} with {self.object}')
            return True
        else:
            print(f'{self.subject} is NOT authorized to {self.action} with {self.object}')
            return False
