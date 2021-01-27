from flask_restx.reqparse import RequestParser

core_request_arguments_parser = RequestParser()
core_request_arguments_parser.add_argument("limit", type=int, location="args")

