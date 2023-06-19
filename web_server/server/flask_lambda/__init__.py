# -*- coding: utf-8 -*-
# Copyright 2016 Matt Martz
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import sys

try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode

from flask import Flask

try:
    from cStringIO import StringIO
except ImportError:
    try:
        from StringIO import StringIO
    except ImportError:
        from io import BytesIO

from flask import Request
from flask_lambda.util import get_nested


__version__ = '0.1.2'


def make_environ(event, context):
    environ = {}
    # key might be there but set to None
    headers = event.get('headers', {}) or {}
    for hdr_name, hdr_value in headers.items():
        hdr_name = hdr_name.replace('-', '_').upper()
        if hdr_name in ['CONTENT_TYPE', 'CONTENT_LENGTH']:
            environ[hdr_name] = hdr_value
            continue

        http_hdr_name = 'HTTP_{}'.format(hdr_name)
        environ[http_hdr_name] = hdr_value

    qs = event.get('queryStringParameters', '')

    environ['REQUEST_METHOD'] = event.get('httpMethod', '')
    environ['PATH_INFO'] = event.get('path', '')
    environ['QUERY_STRING'] = urlencode(qs) if qs else ''
    environ['REMOTE_ADDR'] = get_nested(event, '', 'requestContext', 'identity', 'sourceIp')
    environ['HOST'] = '{}:{}'.format(
        environ.get('HTTP_HOST', ''),
        environ.get('HTTP_X_FORWARDED_PORT', ''),
    )
    environ['SCRIPT_NAME'] = ''
    environ['SERVER_NAME'] = 'SERVER_NAME'

    environ['SERVER_PORT'] = environ.get('HTTP_X_FORWARDED_PORT', '')
    environ['SERVER_PROTOCOL'] = 'HTTP/1.1'

    environ['CONTENT_LENGTH'] = str(
        len(event['body']) if 'body' in event and event['body'] else 0
    )

    environ['wsgi.url_scheme'] = environ.get('HTTP_X_FORWARDED_PROTO', '')
    environ['wsgi.input'] = BytesIO((event['body'] or '').encode())
    environ['wsgi.version'] = (1, 0)
    environ['wsgi.errors'] = sys.stderr
    environ['wsgi.multithread'] = False
    environ['wsgi.run_once'] = True
    environ['wsgi.multiprocess'] = False

    # store AWS input event and context in WSGI environment
    environ['aws.event'] = event
    environ['aws.context'] = context

    return environ


class LambdaRequest(Request):
    @property
    def aws_event(self):
        return self.environ.get('aws.event')

    @property
    def aws_context(self):
        return self.environ.get('aws.context')


class LambdaResponse:

    def __init__(self):
        self.status = None
        self.response_headers = None

    def start_response(self, status, response_headers, exc_info=None):
        self.status = int(status[:3])
        self.response_headers = dict(response_headers)


class FlaskLambda(Flask):
    request_class = LambdaRequest

    def __call__(self, event, context):
        try:
            if 'httpMethod' not in event:
                self.logger.debug('Called as regular Flask app')
                # In this "context" `event` is `environ` and
                # `context` is `start_response`, meaning the request didn't
                # occur via API Gateway and Lambda
                return super(FlaskLambda, self).__call__(event, context)

            self.logger.debug('Called with AWS Lambda input event')
            self.logger.debug('Event: %r', event)

            response = LambdaResponse()

            body = next(self.wsgi_app(
                make_environ(event, context),
                response.start_response
            ))

            return {
                'statusCode': response.status,
                'headers': response.response_headers,
                'body': body.decode('utf-8')
            }

        except:
            self.logger.exception('An unexpected exception occured')

            return {
                'statusCode': 500,
                'headers': {},
                'body': 'Internal Server Error'
            }
