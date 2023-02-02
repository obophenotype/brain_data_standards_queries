import os
import logging
from http import HTTPStatus

from flask import url_for
from flask_restx import Api
from bds_api.exception.api_exception import BDSApiException

log = logging.getLogger(__name__)


# added for https bugfix https://github.com/noirbizarre/flask-restplus/issues/565
class SearchApi(Api):
    @property
    def specs_url(self):
        """Monkey patch for HTTPS"""
        is_https = os.getenv("HTTPS", 'True').lower() in ('true', '1', 't')
        scheme = 'https' if is_https else 'http'
        log.info("Production mode is: " + scheme)
        return url_for(self.endpoint('specs'), _external=True, _scheme=scheme)


api = SearchApi(version='0.0.1', title='BDS Ontology RESTful API',
                description='Brain Data Standards Ontology restful API that wraps search and query endpoints.')


@api.errorhandler
def default_error_handler(e):
    message = 'An unhandled exception occurred.'
    log.exception(message)

    return {'message': message}, HTTPStatus.INTERNAL_SERVER_ERROR


@api.errorhandler(BDSApiException)
def handle_bad_request(error):
    log.exception(error.message)

    return {'message': error.message}, error.status_code


@api.errorhandler(ValueError)
def handle_value_error(error):
    log.exception(str(error))

    return {'message': str(error)}, HTTPStatus.BAD_REQUEST
