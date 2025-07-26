import os
from flask import Flask
from flask_mail import Mail

from src.blueprints.user import app as user_app
from src.blueprints.sql import app as sql_app
from src.blueprints.event import app as event_app
from src.blueprints.registration import app as registration_app
from src.blueprints.docs import app as docs_app
from src.blueprints.image import app as image_app
from src.blueprints.achievements import app as achievements_app
from src.connections import config
from src.constants import HTTP_NOT_FOUND, HTTP_INTERNAL_ERROR
from src.middleware import Middleware
from src.utils.utils import jsonResponse

app = Flask(__name__)
app.config['DEBUG'] = config['debug']
app.wsgi_app = Middleware(app.wsgi_app, url_prefix='/api', cors_origins=config['cors-origins'])

app.register_blueprint(user_app,   url_prefix='/user')
app.register_blueprint(sql_app,  url_prefix='/sql')
app.register_blueprint(event_app,  url_prefix='/event')
app.register_blueprint(registration_app, url_prefix='/registration')
app.register_blueprint(docs_app,   url_prefix='/docs')
app.register_blueprint(image_app,   url_prefix='/image')
app.register_blueprint(achievements_app,   url_prefix='/achievements')

app.config['MAIL_SERVER'] = config['SMTP_mail_server_host']
app.config['MAIL_PORT'] = config['SMTP_mail_server_port']
app.config['MAIL_USE_TLS'] = config['SMTP_mail_server_use_tls']
app.config['MAIL_USERNAME'] = config['mail_address']
app.config['MAIL_DEFAULT_SENDER'] = config['mail_sender_name']
app.config['MAIL_PASSWORD'] = config['mail_password']

mail = Mail(app)


@app.route('/')
def home():
    return "Это начальная страница API для сайта веломаршалов, а не сам сайт. Вiйди отсюда!"


@app.errorhandler(404)
def error404(err):
    print(err)
    return jsonResponse("404 страница не найдена", HTTP_NOT_FOUND)


@app.errorhandler(500)
def error500(err):
    print(err)
    return jsonResponse("500 внутренняя ошибка сервера", HTTP_INTERNAL_ERROR)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', config['port']))
    app.run(port=port, debug=bool(config['debug']))
