from flask import Flask
from threading import *
import aiohttp
import asyncio

app = Flask('')


@app.route('/')
def main():
    return "server online!"


def run():
    app.run(host="0.0.0.0", port=8080)


def website():
    server = Thread(target=run)
    server.start()


async def send_request():
    url = "https://53c9xj-8080.csb.app/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            # لا يوجد حاجة لقراءة الرد أو القيام بأي شيء آخر هنا
            pass
