from flask import Flask, Blueprint
from bds_api import settings
from bds_api.restplus import api
from bds_api.endpoints.search_service import ns as api_namespace
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
# added for https bugfix https://github.com/noirbizarre/flask-restplus/issues/565
app.wsgi_app = ProxyFix(app.wsgi_app)

blueprint = Blueprint('bds', __name__, url_prefix='/bds')


def configure_app(flask_app):
    # flask_app.config['SERVER_NAME'] = settings.FLASK_SERVER_NAME
    flask_app.config['SWAGGER_UI_DOC_EXPANSION'] = settings.RESTPLUS_SWAGGER_UI_DOC_EXPANSION
    flask_app.config['RESTPLUS_VALIDATE'] = settings.RESTPLUS_VALIDATE
    flask_app.config['RESTPLUS_MASK_SWAGGER'] = settings.RESTPLUS_MASK_SWAGGER
    flask_app.config['ERROR_404_HELP'] = settings.RESTPLUS_ERROR_404_HELP


def initialize_app(flask_app):
    configure_app(flask_app)
    api.init_app(blueprint)
    api.add_namespace(api_namespace)
    flask_app.register_blueprint(blueprint)


def main():
    initialize_app(app)
    app.run(host="0.0.0.0", port=8080, debug=settings.FLASK_DEBUG)


if __name__ == '__main__':
    main()
