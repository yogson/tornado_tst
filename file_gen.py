import os
import random
import string
from multiprocessing import Pool
from time import time


def get_random_string(*args, length=1000**2):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for _ in range(length))


def gen_file(file_path, file_len):
    with open(file_path, 'w') as f:
        with Pool(os.cpu_count()) as p:
            f.writelines(p.map(get_random_string, range(file_len)))


start_time = time()
gen_file('/home/yogson/Nextcloud/PycharmProjects/tornado_tst/5.txt', 500)
print(round(time()-start_time, 2))