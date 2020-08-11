import inspect
import os
import re

# Если очень захотим базовых хардкодных хэндлеров - раскоментить
# from handlers import HeartBeat, HugeFileHandler
# BASE_ENDPOINTS = [
#     (r'/', HeartBeat),
#     (r'/([.a-zA-Z0-9]*)', HugeFileHandler, {'path': '/Users/egor/Downloads'})
# ]

HANDLERS_PATH = '.'
HANDLERS_FILE_RE = r'^handlers.*\.py$'


def get_module_names():
    return [f.replace('.py', '') for f in os.listdir(HANDLERS_PATH) if re.search(HANDLERS_FILE_RE, f)]


def get_handler(cls: tuple) -> tuple:
    _, kls = cls  # берём из тапла только нужное
    assert hasattr(kls, 'URI')  # если нет адреса эндпоинта: эксепшн

    if hasattr(kls, 'PARAMS'):
        return kls.URI, kls, kls.PARAMS
    else:
        return kls.URI, kls


def get_classes(module_name: str) -> list:
    module = __import__(module_name)
    return inspect.getmembers(
        module, lambda member: inspect.isclass(member) and member.__module__ == module.__name__
    )


def get_endpoints(file_names: list) -> list:
    endpoints = []

    for fn in file_names:
        endpoints += [get_handler(cls) for cls in get_classes(fn)]

    return endpoints


ENDPOINTS = get_endpoints(get_module_names())
