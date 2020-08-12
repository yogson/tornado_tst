import random
import string
import asyncio
from multiprocessing import Pool
from time import time

import aiofiles


def get_random_string(_, length=1000**2):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for _ in range(length))


async def gen_file_multi(file_path, file_len):
    with Pool(12) as p:
        async with aiofiles.open(file_path, 'w') as f:
            await f.writelines(p.map(get_random_string, range(file_len)))


async def gen_file_mono(file_path, file_len):
    async with aiofiles.open(file_path, 'w') as f:
        await f.writelines((get_random_string(0) for _ in range(file_len)))


start_time = time()
asyncio.run(gen_file_multi('/home/yogson/Nextcloud/PycharmProjects/tornado_tst/1.txt', 1000))
print(round(time()-start_time, 2))