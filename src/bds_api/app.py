from flask import Flask, Blueprint
from bds_api import settings
from bds_api.restplus import api
from bds_api.endpoints.search_service import ns as api_namespace
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
# added for https bugfix https://github.com/noirbizarre/flask-restplus/issues/565
app.wsgi_app = ProxyFix(app.wsgi_app)

blueprint = Blueprint('bds', __name__, url_prefix='/bds')


def initialize_app(flask_app):
    api.init_app(blueprint)
    api.add_namespace(api_namespace)
    flask_app.register_blueprint(blueprint)


def main():
    initialize_app(app)
    app.run(host="0.0.0.0", port=8080, debug=settings.FLASK_DEBUG)
    # TODO just testing https here (add pyopenssl to requirements.txt)
    # app.run(host="0.0.0.0", port=8080, debug=settings.FLASK_DEBUG, ssl_context='adhoc')


if __name__ == '__main__':
    main()
