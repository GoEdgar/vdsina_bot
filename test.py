import aiohttp
import asyncio



async def f():
    async with aiohttp.ClientSession(headers='g') as sess:
        print(type(sess.head()))
        html = await sess.get('http://google.com')
        print( await html.text())
        
        
loop = asyncio.get_event_loop()
loop.run_until_complete(f())