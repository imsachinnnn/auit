"""
Cloudflare R2 Storage Backend for Django
Uses S3-compatible API to store files in Cloudflare R2
"""
import os
from storages.backends.s3boto3 import S3Boto3Storage


class R2Storage(S3Boto3Storage):
    """
    Custom storage backend for Cloudflare R2.
    Configured to use R2's S3-compatible API.
    """
    # R2 Configuration from environment variables
    access_key = os.getenv('R2_ACCESS_KEY_ID')
    secret_key = os.getenv('R2_SECRET_ACCESS_KEY')
    bucket_name = os.getenv('R2_BUCKET_NAME')
    endpoint_url = os.getenv('R2_ENDPOINT_URL')
    custom_domain = os.getenv('R2_PUBLIC_URL', None)  # Optional CDN URL
    
    # R2-specific settings
    region_name = 'auto'  # R2 uses 'auto' for region
    file_overwrite = False  # Don't overwrite existing files
    default_acl = None  # R2 doesn't use ACLs like S3
    
    # Performance settings
    object_parameters = {
        'CacheControl': 'max-age=86400',  # Cache for 1 day
    }
    
    def __init__(self, **settings):
        super().__init__(**settings)

