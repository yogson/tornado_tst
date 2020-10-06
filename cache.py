import _collections_abc
import threading
from copy import deepcopy
from collections import OrderedDict
from datetime import datetime, timedelta
from abc import abstractmethod, ABC
import json
from time import sleep

from redis import Redis
import psycopg2


class CustomOrderedDict(OrderedDict):

    def __init__(self):
        super().__init__()

    @property
    def older(self):
        for k, v in self.items():
            return k, v


class CacheInterface(ABC):
    """
    Caching system interface class.
    Please, implement touch, delete, put and get methods.

    """

    def __init__(self, realm):
        self.realm = realm

    @abstractmethod
    def touch(self):
        """implement cache touch method"""
        pass

    @abstractmethod
    def get(self, key):
        """ implement cache get method"""
        pass

    @abstractmethod
    def put(self, key, value):
        """ implement cache put method"""
        pass

    def get_or_renew(self, key, renewal_callable):
        """
        Utility function to get data from the cache or if absent call renew function.
        :param key: str
        :param renewal_callable: callable
        :return: cache value
        """
        result = self.get(key)
        if not result and renewal_callable:
            result = renewal_callable()
            self.put(key, result)
        return result


class LocalCache(CacheInterface):
    """
    Caching interface realization to keep the data in app's memory while ttl
    """

    def __init__(self, realm):
        super().__init__(realm)
        self.container = CustomOrderedDict()

    def put(self, key, value):
        if self.realm.max_length and len(self.container) >= self.realm.max_length:
            for _ in range(int(self.realm.max_size/100*10)):
                self.pop()
        if self.realm.max_size and self.container.__sizeof__() >= self.realm.max_size:
            while self.container.__sizeof__() > self.realm.max_size/100*90:
                self.pop()
        self.container[key] = value, datetime.now() + timedelta(seconds=self.realm.ttl)

    def get(self, key):
        result = self.container.get(key)
        if not result:
            return
        expired = datetime.now() >= result[1]
        if expired:
            return
        return deepcopy(result[0])

    def delete(self, key):
        self.container.pop(key)

    def pop(self):
        self.container.popitem(last=False)

    def touch(self):
        older = self.container.older
        while older:
            if older[1][1] <= datetime.now():
                self.delete(older[0])
                older = self.container.older
            else:
                break


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
    default_max_length = 1000
    default_max_size = 1024
    default_interface = LocalCache
    default_sleep_time = 60

    def __init__(self, auto_purge=False):
        self.realms = dict(
            default=KeyValueTimedCache.Realm(
                'default', self.default_ttl,  self.default_interface, self.default_max_size
            )
        )
        if auto_purge:
            t = threading.Thread(target=self._touch_realms, args=(self.default_sleep_time, ), daemon=True)
            t.start()

    def __getitem__(self, key):
        return self.realms.get(key)

    def _touch_realms(self, sleep_time):
        while True:
            for realm in self.realms.values():
                realm.touch()
            sleep(sleep_time)

    def new_realm(
            self, name,
            ttl=default_ttl,
            interface=default_interface,
            max_length=default_max_length,
            max_size=default_max_size
    ):
        self.realms.update(
            {
                name: KeyValueTimedCache.Realm(name, ttl, interface, max_length, max_size)
            }
        )
        return self.realms[name]

    def get(self, realm: str, key, absent=None, renewal=None):
        if realm in self.realms:
            result = self.realms[realm].get(key, absent, renewal)
            return result

    def put(self, realm: str, key, value):
        if realm not in self.realms:
            self.new_realm(
                realm, self.default_ttl, self.default_interface, self.default_max_length, self.default_max_size
            )
        self.realms[realm][key] = value

    class Realm:

        def __init__(
                self,
                name: str,
                ttl: int,
                interface: type,
                max_length: int = None,
                max_size: int = None
        ):

            self.max_length = max_length
            self.ttl = ttl
            self.max_size = max_size
            self.name = name
            self.interface = interface(self)
            self._put = self.interface.put
            self._get = self.interface.get_or_renew

            assert isinstance(self.interface, CacheInterface)

        def __setitem__(self, key, value):
            self.touch()
            assert isinstance(key, str)
            self._put(key, serialize(value))

        def __getitem__(self, key, renewal=None):
            self.touch()
            item = self._get(key, renewal)
            return deserialize(item) if item else item

        def get(self, key, absent=None, renewal=None):
            result = self.__getitem__(key, renewal) or absent
            return result

        def touch(self):
            self.interface.touch()


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


class PgCache(CacheInterface):

    user = 'pythoner'
    password = 'kal1966'
    master = True

    def __init__(self, realm):
        super().__init__(realm)
        self.conn = psycopg2.connect(
            database='tst',
            user=self.user,
            password=self.password
        )
        self.table_name = 'pg_cache_'+self.realm.name
        self.cur = self.conn.cursor()
        if not self._table_exists(self.realm.name):
            query = f"""
            CREATE TABLE {self.table_name}  
                (id serial PRIMARY KEY, key varchar UNIQUE, value varchar, expires_at timestamp);
            """
            self.cur.execute(query)
            self.conn.commit()

    def _table_exists(self, table_name):
        query = """
        SELECT EXISTS (
                       SELECT FROM information_schema.tables
                       WHERE table_name = %s
                       );
        """
        self.cur.execute(query, (table_name, ))
        resp = self.cur.fetchone()
        if isinstance(resp, tuple):
            return resp[0]

    def _sql_write(self, query: str, args: tuple) -> None:
        self.cur.execute(query, args)
        self.conn.commit()

    def _sql_read(self, query: str, args: tuple) -> list:
        self.cur.execute(query, args)
        return self.cur.fetchall()

    def put(self, key, value):
        query = f"""
        INSERT INTO {self.table_name} (key, value, expires_at) 
        VALUES (%s, %s, %s)
        ON CONFLICT (key) DO UPDATE 
        SET value = excluded.column_1, ;
        """
        self._sql_write(query, (key, value, datetime.now() + timedelta(seconds=self.realm.ttl)))

    def get(self, key):
        query = f"""
        SELECT value, expires_at FROM {self.table_name} 
        WHERE (key = %s);
        """
        result = self._sql_read(query, (key, ))
        return result[0][0] if datetime.now() < result[0][1] else None

    def touch(self):
        pass
