# storages.py
from storages.backends.s3boto3 import S3Boto3Storage

class ImageStorage(S3Boto3Storage):
    bucket_name = 'post-manito'  # Nombre de tu bucket
    custom_domain = f'{bucket_name}.s3.amazonaws.com'
    file_overwrite = False
    default_acl = None