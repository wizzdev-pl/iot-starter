from http import HTTPStatus

import flask


def _create_common_response(data, status: int, status_text: str):
    response_dict = {
        'data': data,
        'status': status,
        'status_text': status_text,
    }
    return flask.jsonify(response_dict)


def create_success_response(data: dict or list, status: int = None, status_text: str = None):
    return _create_common_response(data=data,
                                   status=status or HTTPStatus.OK.value,
                                   status_text=status_text or HTTPStatus.OK.description)


def create_success_plain_response(status_text: str = None):
    return flask.Response(status_text or HTTPStatus.NO_CONTENT.description,
                          status=HTTPStatus.NO_CONTENT.value,
                          mimetype='text/plain')


def create_failed_response(status_text: str = None):
    return flask.Response(status_text or HTTPStatus.INTERNAL_SERVER_ERROR.description,
                          status=HTTPStatus.INTERNAL_SERVER_ERROR.value,
                          mimetype='text/plain')


def create_not_found_response():
    return flask.Response(HTTPStatus.NOT_FOUND.description,
                          status=HTTPStatus.NOT_FOUND.value,
                          mimetype='text/plain')


def create_invalid_request_data_response(status_text=None):
    return flask.Response(status_text or HTTPStatus.BAD_REQUEST.description,
                          status=HTTPStatus.BAD_REQUEST.description,
                          mimetype='text/plain')
