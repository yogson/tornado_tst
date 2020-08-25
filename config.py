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
    kls_name, kls = cls

    if kls_name and kls_name.__contains__('Handler'):
        assert hasattr(kls, 'URI'), f'Handler class {kls} must contain endpoint URI'  # если нет адреса эндпоинта: эксепшн

        if hasattr(kls, 'PARAMS'):
            return kls.URI, kls, kls.PARAMS
        else:
            return kls.URI, kls


def get_classes(module_name: str) -> list:
    try:
        module = __import__(module_name)
    except ModuleNotFoundError as e:
        return get_classes(module_name) if install_dep(e.name, module_name) else []

    return inspect.getmembers(
        module,
        lambda member: inspect.isclass(member) and member.__module__ == module.__name__
    )


def install_dep(dep_name: str, module_name: str) -> bool:
    import pip

    print(f'Dependency not found in module {module_name}: {dep_name}. Will try to install...')
    res = pip.main(['install', dep_name])

    if res == 0:
        print(dep_name, 'successfully installed')
        return True
    else:
        print(f'Unable to install {dep_name}. Module {module_name} will be disabled.')
        return False


def get_endpoints(file_names: list) -> list:
    endpoints = []

    for fn in file_names:
        endpoints += [get_handler(cls) for cls in get_classes(fn) if get_handler(cls)]

    return endpoints


ENDPOINTS = get_endpoints(get_module_names())
