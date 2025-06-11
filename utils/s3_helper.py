# utils/s3_helper.py
import boto3

def download_image_from_s3(bucket_name, key, download_path):
    s3 = boto3.client('s3')
    s3.download_file(bucket_name, key, download_path)
