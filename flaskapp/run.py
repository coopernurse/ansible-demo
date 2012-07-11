#!/usr/bin/env python

from flask import Flask
import socket

app = Flask(__name__)

ips = [ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")]
my_ip = ips[0]

@app.route("/")
def hello():
    return "Hello from server: %s" % ip

if __name__ == "__main__":
    app.run()
