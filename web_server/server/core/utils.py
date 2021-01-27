import flask
import typing

from config import PAGE_SIZE
from service.base_service import BaseService
from core.request_arguments_parser import core_request_arguments_parser


def add_no_robots_html_header(response: flask.Response):
    response.headers['X-Robots-Tag'] = "noindex, nofollow, noarchive"
    return response


def scan_with_pagination(service: typing.Type[BaseService], **kwargs):
    args = core_request_arguments_parser.parse_args()
    return service.scan(limit=args.limit or PAGE_SIZE, **kwargs)
