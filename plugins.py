import inspect
import os
import re
import importlib
import sys

PLUGINS_PATH = './plugins'
HANDLERS_FILE_RE = r'^.*handlers.*.py$'


def get_plugins():
    plugins = []

    for plugin in (dir_ for dir_ in os.listdir(PLUGINS_PATH)):
        plugins.append(
            {
                plugin: [
                    f.replace('.py', '') for f in os.listdir(
                        os.path.join(PLUGINS_PATH, plugin)
                    ) if re.search(HANDLERS_FILE_RE, f)
                ]
            }
        )

    return plugins


def get_handler(cls: tuple) -> tuple:
    kls_name, kls = cls

    if kls_name and kls_name.__contains__('Handler'):
        assert hasattr(kls, 'URI'), f'Handler class {kls} must contain endpoint URI'  # если нет адреса эндпоинта: эксепшн

        if hasattr(kls, 'PARAMS'):
            return kls.URI, kls, kls.PARAMS
        else:
            return kls.URI, kls


def get_classes(package_name: str, modules: list) -> list:
    classes = []

    for module_name in modules:
        try:
            module = importlib.import_module(f'.{module_name}', package=package_name)
        except ModuleNotFoundError as e:
            print(e)
            return get_classes(module_name, modules) if install_dep(e.name, module_name) else []

        classes += inspect.getmembers(
            module,
            lambda member: inspect.isclass(member) and member.__module__ == module.__name__
        )

    return classes


def install_dep(dep_name: str, module_name: str) -> bool:
    import pip

    #  TODO Logging, not printing
    print(f'Dependency not found in module {module_name}: {dep_name}. Will try to install...')
    res = pip.main(['install', dep_name])

    if res == 0:
        print(dep_name, 'successfully installed')
        return True
    else:
        print(f'Unable to install {dep_name}. Module {module_name} will be disabled.')
        return False


def get_endpoints(plugins: list) -> list:
    endpoints = []

    for plugin in plugins:
        for package, modules in plugin.items():
            endpoints += [get_handler(cls) for cls in get_classes(package, modules) if get_handler(cls)]

    return endpoints


sys.path.append(PLUGINS_PATH)
ENDPOINTS = get_endpoints(get_plugins())
