import hashlib
import hmac
import json
from base64 import b64encode
from datetime import datetime, timedelta

from flask import current_app
from boto.s3.cors import CORSConfiguration
from boto.exception import S3ResponseError


def enable_bucket_cors(bucket):
    """ For direct upload to work, the bucket needs to enable
    cross-origin request scripting. """
    try:
        cors_cfg = bucket.get_cors()
    except S3ResponseError:
        cors_cfg = CORSConfiguration()
    rules = [r.id for r in cors_cfg]
    changed = False
    if 'spendb_put' not in rules:
        cors_cfg.add_rule(['PUT', 'POST'], '*',
                          allowed_header='*',
                          id='spendb_put',
                          max_age_seconds=3000,
                          expose_header='x-amz-server-side-encryption')
        changed = True
    if 'spendb_get' not in rules:
        cors_cfg.add_rule('GET', '*', id='spendb_get')
        changed = True

    if changed:
        bucket.set_cors(cors_cfg)


def generate_s3_upload_policy(source, file_name, mime_type):
    """ Generate a policy and signature for uploading a file directly to
    the specified source on S3. """
    obj = source._obj
    if not hasattr(obj, 'key'):
        return {
            'status': 'error',
            'message': 'Backend is not on S3, cannot generate signature.'
        }

    enable_bucket_cors(obj.store.bucket)
    url = obj.key.generate_url(expires_in=0, force_http=True,
                               query_auth=False)
    url = url.split(obj.key.name)[0]

    if 'https' in current_app.config.get('PREFERRED_URL_SCHEME'):
        url = url.replace('http://', 'https://')

    data = {
        'url': url,
        'status': 'ok',
        'key': obj.key.name,
        'source_name': source.name,
        'aws_key_id': obj.store.aws_key_id,
        'acl': 'public-read',
        'file_name': file_name,
        'mime_type': mime_type
    }
    expire = datetime.utcnow() + timedelta(days=7)
    expire, ms = expire.isoformat().split('.')
    policy = {
        "expiration": expire + "Z",
        "conditions": [
            {"bucket": obj.store.bucket_name},
            ["starts-with", "$key", data['key']],
            {"acl": data['acl']}
        ]
    }

    # data['raw_policy'] = json.dumps(policy)
    data['policy'] = b64encode(json.dumps(policy))
    data['signature'] = b64encode(hmac.new(obj.store.aws_secret,
                                           data['policy'],
                                           hashlib.sha1).digest())
    return data
