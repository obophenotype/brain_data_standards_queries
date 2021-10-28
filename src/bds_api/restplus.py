import logging
from http import HTTPStatus

from flask_restplus import Api
from bds_api.exception.api_exception import BDSApiException

log = logging.getLogger(__name__)

api = Api(version='0.0.1', title='BDS Ontology RESTful API',
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
