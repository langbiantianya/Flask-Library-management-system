from flask import Flask
from App.extension import init_ext
from App.apis import init_api
from App import settings,models

def creat_app():
    app = Flask(__name__)
    app.config.from_object(settings.Develop)
    init_api(app)
    init_ext(app)

    return app