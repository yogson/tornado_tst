from abc import ABC
from datetime import datetime
from os.path import join, isfile, getsize

import aiofiles
from tornado import iostream, gen
from tornado.web import RequestHandler


class HeartBeatHandler(RequestHandler, ABC):

    URI = r'/'

    async def get(self):
        self.write(datetime.strftime(datetime.now(), '%d.%m.%Y %H:%M:%S')+' OK\n')
        await self.flush()
        await gen.sleep(0.0001)


class HugeFileHandler(RequestHandler, ABC):

    URI = r'/download/([.a-zA-Z0-9]*)'
    PARAMS = {'path': '/home/yogson/Nextcloud/PycharmProjects/tornado_tst/media'}

    def initialize(self, **kwargs):
        self.path = kwargs.get('path')

    async def get(self, file_name):
        file_path = join(self.path, file_name)
        if isfile(file_path):
            h = {
                "Content-Description": "File Transfer",
                "Content-type": "application/octet-stream",
                "Content-Disposition": f"attachment; filename={file_name}_COPY",
                "Content-Transfer-Encoding": "binary",
                "Content-Length": getsize(file_path)
            }
            for header, value in h.items():
                self.set_header(header, value)
            print('Uploading', file_name, 'to', self.request.remote_ip)
            async with aiofiles.open(file_path, mode='rb') as f:
                while True:
                    chunk = await f.read((1024**2)*10)
                    if chunk is None:
                        break
                    try:
                        self.write(chunk)
                        await self.flush()
                    except iostream.StreamClosedError:
                        break
                    finally:
                        del chunk
                        await gen.sleep(0.0001)
        else:
            self._reason = f'File {file_name} not found'
            self.write_error(404)
        print('Finished', file_name)

