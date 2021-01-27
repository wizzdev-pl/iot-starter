import os

IOT_AWS_REGION = os.environ.get('IOT_AWS_REGION', 'eu-west-2')

DATABASE_PREFIX = os.environ.get('DATABASE_PREFIX', 'db')  # Used in process of DynamoDB generating tables name
DATABASE_HOST = os.environ.get('DATABASE_HOST', None)  # Add host if want local connection

DEBUG = bool(os.environ.get('DEBUG', False))
