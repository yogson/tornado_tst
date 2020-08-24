import os
import random
import string
from multiprocessing import Pool
from time import time
import asyncio

import aiofiles


def get_random_string(*args, length=1000**2):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for _ in range(length))


def gen_file_multi_map(file_path, file_len):
    with open(file_path, 'w') as f:
        with Pool(os.cpu_count()) as p:
            f.writelines(p.map(get_random_string, range(file_len)))


async def gen_file_multi_app(file_path, file_len):
    async with aiofiles.open(file_path, 'w') as f:
        with Pool(os.cpu_count()) as p:
            for _ in range(file_len):
                await f.write(p.apply_async(get_random_string).get())


def gen_file_mono(file_path, file_len):
    with open(file_path, 'w') as f:
        f.writelines((get_random_string(0) for _ in range(file_len)))


start_time = time()
gen_file_multi_map('/home/yogson/Documents/media/7.txt', 1500)
print(round(time()-start_time, 2))