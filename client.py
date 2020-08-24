from time import sleep, time

import aiohttp
import asyncio


async def fetch(client):
    start = time()
    try:
        async with client.get('http://127.0.0.1:8888') as resp:
            data = await resp.text()
            fin = time()
            assert resp.status == 200
            return fin - start, data
    except Exception as e:
        return 0, e


async def main():
    async with aiohttp.ClientSession() as client:
        longest_time = - float('inf')
        acc = 0
        i = 0
        while True:
            i += 1
            req_time, html = await fetch(client)
            longest_time = req_time if longest_time < req_time else longest_time
            acc += req_time
            print('{:.4f}'.format(req_time), html)
            if i % 10 == 0:
                print('average time:', '{:.4f}'.format(acc / i), 'longest time:', '{:.4f}'.format(longest_time))
            sleep(1)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
