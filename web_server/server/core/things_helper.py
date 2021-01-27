import os
import warnings
import boto3
import requests

import config
from botocore.config import Config as boto_config
from core.certificates_helper import CertificatesHandler

aws_config = boto_config(region_name=config.AWS_REGION)
thing_client = boto3.client('iot', config=aws_config)


def create_thing(device_data: dict):
    thing_data = get_thing_data_from_device_data(device_data)
    delete_thing_if_exist(thing_data['thingName'])
    create_response = thing_client.create_thing(**thing_data, thingTypeName=config.AWS_BASE_THING_TYPE)


def get_thing_data_from_device_data(device_data: dict) -> dict:
    """
    Device parameters are mapped into things parameters:
        - device_id == thingName
        - device_type == thingType
        - settings == attributes
    Merge is always false
    """
    thing_data = {}
    thing_data['thingName'] = device_data.get('device_id')
    thing_data['attributePayload'] = {}
    thing_data['attributePayload']['attributes'] = device_data.get('settings')
    thing_data['attributePayload']['merge'] = False
    return thing_data


def create_thing_type_if_not_exist(thing_type: str):
    warnings.warn("API isn't responsible for creating new thing types anymore", DeprecationWarning)
    return


def create_billing_group_if_not_exist(billing_group: str):
    warnings.warn("API isn't responsible for creating new billing groups anymore", DeprecationWarning)
    return


def delete_thing_if_exist(thing_name: str):
    try:
        thing_client.describe_thing(thingName=thing_name)
    except thing_client.exceptions.ResourceNotFoundException as e:
        thing_client.delete_thing(thingName=thing_name)


def get_thing_certificates(thing_name: str):
    certs_handler = CertificatesHandler(thing_client)
    certs = certs_handler.get_certificates()
    thing_client.attach_thing_principal(thingName=thing_name, principal=certs_handler.cert_arn)
    thing_client.attach_principal_policy(principal=certs_handler.cert_arn, policyName=config.AWS_BASE_THING_POLICY)
    return certs
