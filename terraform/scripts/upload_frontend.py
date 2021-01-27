"""
The utility script that upload all files from provided directory to desire S3 bucket
To run this script you need to obtain S3 related permissions.
Script detects and adds mime types for html, css and javascript files only.
It's configurable with following parameters:
S3_BUCKET (required) name of S3 bucket
BUILD_DIR (required) path to input directory
-v, --verbose (optional) set logging level
"""

import os, pathlib
import argparse
import logging

import boto3


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("S3_BUCKET")
    parser.add_argument("BUILD_DIR")
    parser.add_argument("-v", "--verbose", type=str, choices=["DEBUG", "INFO", "WARNING", "ERROR"], default="INFO")
    return parser.parse_args()


def get_content_type(path: str):
    if not isinstance(path, str):
        path = str(path)
    if path.endswith('html'):
        return 'text/html'
    if path.endswith('css'):
        return 'text/css'
    if path.endswith('js'):
        return 'text/javascript'


def upload_package(build_dir_path, s3_bucket):
    s3 = boto3.client('s3')
    bucket_entries = s3.list_objects_v2(Bucket=s3_bucket).get('Contents', [])
    for entry in bucket_entries:
        s3.delete_object(Bucket=s3_bucket, Key=entry['Key'])
    for root, dirs, files in os.walk(build_dir_path):
        for file in files:
            name = os.path.join(root, file).replace(str(build_dir_path), "")
            if name.startswith('\\'):
                name = name[1:]
            if name.startswith('/'):
                name = name[1:]
            name = name.replace('\\', '/')
            content_type = get_content_type(name)
            extra_args = {
                'ACL': 'public-read',
            }
            if content_type:
                extra_args['ContentType'] = content_type
            logging.info(f"Uploading {name}")
            s3.upload_file(os.path.join(root, file), s3_bucket, name, ExtraArgs=extra_args)


if __name__ == '__main__':
    args = parse_args()
    logging.basicConfig(level=args.verbose)
    # Paths
    build_dir = pathlib.Path(args.BUILD_DIR).resolve().absolute()
    s3_bucket = args.S3_BUCKET
    logging.info(f"Resolve arguments: \n BUILD_DIR: {build_dir} \n S3 BUCKET: {s3_bucket}")
    # Upload
    upload_package(build_dir, s3_bucket)
