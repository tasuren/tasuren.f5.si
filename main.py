""" tasuren's web server
Powered by sanic
           ▄▄▄▄▄
        ▀▀▀██████▄▄▄      _______________
      ▄▄▄▄▄  █████████▄  /               \
     ▀▀▀▀█████▌ ▀▐▄ ▀▐█ | Gotta go fast! |
   ▀▀█████▄▄ ▀██████▄██ | _______________/
   ▀▄▄▄▄▄  ▀▀█▄▀█════█▀ |/
        ▀▀▀▄  ▀▀███ ▀       ▄▄
     ▄███▀▀██▄████████▄ ▄▀▀▀▀▀▀█▌
   ██▀▄▄▄██▀▄███▀ ▀▀████      ▄██
▄▀▀▀▄██▄▀▀▌████▒▒▒▒▒▒███     ▌▄▄▀
▌    ▐▀████▐███▒▒▒▒▒▐██▌
▀▄▄▄▄▀   ▀▀████▒▒▒▒▄██▀
          ▀▀█████████▀
        ▄▄██▀██████▀█
      ▄██▀     ▀▀▀  █
     ▄█             ▐▌
 ▄▄▄▄█▌              ▀█▄▄▄▄▀▀▄
▌     ▐                ▀▀▄▄▄▀
 ▀▀▄▄▀                           """

from json import load, loads, dumps
from aiofile import async_open
from os.path import exists

from sanic.response import file, html, redirect
from sanic.exceptions import abort, NotFound
from sanic import Sanic

from jinja2 import Environment, FileSystemLoader, select_autoescape
from flask_misaka import Misaka


with open("data.json", "r", encoding="utf-8_sig") as f:
    data = load(f)


SSL = {
    "cert": "static/certificate.crt",
    "key": "static/private.key",
    "verify": "static/ca_certs.crt"
}
SSL = None
PORT = 80
HOST = "0.0.0.0"


app = Sanic("RT-WebSite")

app.static("/static", "static")


# Jinja2 テンプレートエンジン。
env = Environment(loader=FileSystemLoader("./templates"),
                  autoescape=select_autoescape(['html', 'xml', 'tpl']),
                  enable_async=True)


async def template(tpl, **kwargs):
    template = env.get_template(tpl)
    content = await template.render_async(kwargs)
    return html(content)


# Flask-MisakaをJinja2にくっつける。
# マークダウンレンダリング用。
md = Misaka(
    autolink=True, wrap=True)
env.filters.setdefault("markdown", md.render)


# ===  MAIN ## === #
@app.route('/')
async def index(request):
    return redirect("/index.html")


@app.route("/favicon.ico")
async def favicon(request):
    return await file("static/favicon.ico")


@app.route('/<name>.html')
async def normal(request, name):
    if name == "menu":
        return await template('menu.html')
    try:
        if name[0] == "_":
            return await template(name + '.html')
        else:
            return await template('index.html', file_name=name, title=data["titles"].get(name))
    except NotFound:
        return await abort(404)


app.run(host=HOST, port=PORT, ssl=SSL)