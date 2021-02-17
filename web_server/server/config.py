import os


SECRET_KEY = os.environ.get("SECRET_KEY", "secretX@0486791020945248")
PAGE_SIZE = int(os.environ.get('PAGE_SIZE', 15))
NO_ROBOTS = bool(os.environ.get('NO_ROBOTS', True))  # Define if page should be indexed
CORS = bool(os.environ.get('CORS', True))
ENV_LOGIN = os.environ.get('ESP_HARD_LOGIN', 'DEBUG_LOGIN')
ENV_PASSWORD = os.environ.get('ESP_HARD_PASSWORD', 'DEBUG_PASSWORD')
AWS_ROOT_CA_CERTIFICATE_URL = "https://www.amazontrust.com/repository/AmazonRootCA1.pem"
AWS_REGION = os.environ.get('API_REGION_AWS')
AWS_BASE_THING_TYPE = os.environ.get('THING_TYPE_BASE_AWS')
AWS_BASE_THING_POLICY = os.environ.get('THING_POLICY_BASE_AWS')
