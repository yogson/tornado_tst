from copy import deepcopy
from datetime import datetime, timedelta
from abc import abstractmethod, ABC
import json

from redis import Redis


class CacheInterface(ABC):
    """
    Caching system interface class.
    Please, implement put and get methods.

    """

    def __init__(self, realm):
        self.realm = realm

    @abstractmethod
    def get(self, key):
        """ implement cache get method"""
        pass

    @abstractmethod
    def put(self, key, value):
        """ implement cache put method"""
        pass

    def get_or_renew(self, key, renew_value):
        """
        Utility function to get data from the cache or if absent call renew function.
        :param key: str
        :param renew_value: callable
        :return: cache value
        """
        result = self.get(key)
        if not result and renew_value:
            result = renew_value()
            self.put(key, result)
        return result


class LocalCache(CacheInterface):
    """
    Caching interface realization to keep the data in app's memory while ttl
    """

    def __init__(self, realm):
        super().__init__(realm)
        self.container = dict()

    def put(self, key, value):
        self.container[key] = self.TimedValue(value, self.realm.ttl)

    def get(self, key):
        result = self.container.get(key)
        return result.value if result else None

    class TimedValue:
        """Class to keep value while not ttl has expired"""

        def __init__(self, value, ttl):
            self.expiration = datetime.now() + timedelta(seconds=ttl)
            self._value = value

        @property
        def expired(self):
            if datetime.now() >= self.expiration:
                return True
            return False

        @property
        def value(self):
            if self.expired:
                self._value = None
            return deepcopy(self._value) if self._value else None

        def update(self, *args, **kwargs):
            raise SyntaxError


def serialize(data):
    #  Here goes serialization procedure
    result = json.dumps(data)
    return result


def deserialize(data: str):
    #  Here goes deserialization procedure
    result = json.loads(data)
    return result


class KeyValueTimedCache:
    """
    Cache manager class.
    Realms are scopes of data with specified ttl and caching interface realization.
    You can have in your app certain different cache types simultaneously.
    """

    # TODO move to config
    default_ttl = 60
    default_interface = LocalCache

    def __init__(self):
        self.realms = dict(
            default=KeyValueTimedCache.Realm('default', self.default_ttl, self.default_interface)
        )

    def __getattr__(self, item):
        return self.realms.get(item)

    def __getitem__(self, item):
        return self.__getattr__(item)

    def new_realm(self, name, ttl=default_ttl, interface=default_interface):
        self.realms.update(
            {
                name: KeyValueTimedCache.Realm(name, ttl, interface)
            }
        )

    def get(self, realm: str, key, absent=None, renewal=None):
        if realm in self.realms:
            result = self.realms[realm].get(key, absent, renewal)
            return result

    def put(self, realm: str, key, value):
        if realm not in self.realms:
            self.new_realm(realm, self.default_ttl, self.default_interface)
        self.realms[realm][key] = value

    class Realm:

        def __init__(
                self,
                name: str,
                ttl: int,
                interface: type
        ):

            self.ttl = ttl
            self.name = name
            self.interface = interface(self)
            self._put = self.interface.put
            self._get = self.interface.get_or_renew

            assert isinstance(self.interface, CacheInterface)

        def __setitem__(self, key, value):
            assert isinstance(key, str)
            self._put(key, serialize(value))

        def __getitem__(self, key, renewal=None):
            item = self._get(key, renewal)
            return deserialize(item) if item else item

        def get(self, key, absent=None, renewal=None):
            result = self.__getitem__(key, renewal) or absent
            return result


class RedisCache(CacheInterface):
    """
    Cache interface implementation using Redis to keep the data while not ttl has passed.
    """

    realm_index = -1

    def __new__(cls, *args, **kwargs):
        cls.realm_index += 1
        return object.__new__(cls)

    def __init__(self, realm, **kwargs):
        super().__init__(realm)
        self._redis = Redis(db=self.realm_index, **kwargs)
        self._redis.flushdb()

    def put(self, key, value):
        self._redis.mset(
            {key: value}
        )
        self._redis.expireat(
            key,
            datetime.now() + timedelta(seconds=self.realm.ttl)
        )

    def get(self, key):
        return self._redis.get(key)
