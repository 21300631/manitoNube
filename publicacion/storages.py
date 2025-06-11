from storages.backends.s3boto3 import S3Boto3Storage

class ImageStorage(S3Boto3Storage):
    bucket_name = 'post-manito'
    custom_domain = f'{bucket_name}.s3.amazonaws.com'
    file_overwrite = False
    default_acl = None  # Esto es crucial para buckets con ACLs deshabilitadas