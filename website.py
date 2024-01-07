from flask import Flask
from threading import *

app = Flask('')


@app.route('/')
def main():
    return "server online!"


def run():
    app.run(host="0.0.0.0", port=8080)


def website():
    server = Thread(target=run)
    server.start()
