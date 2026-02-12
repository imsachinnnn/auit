
import os
from dotenv import load_dotenv

# Try loading .env explicitly
load_dotenv()

r2_public = os.getenv('R2_PUBLIC_URL')
r2_endpoint = os.getenv('R2_ENDPOINT_URL')
account_id = os.getenv('R2_ACCOUNT_ID')

print(f"R2_PUBLIC_URL: '{r2_public}'")
print(f"R2_ENDPOINT_URL: '{r2_endpoint}'")
if r2_public == r2_endpoint:
    print("WARNING: Public URL is same as Endpoint URL. This is likely wrong.")

import django
from django.conf import settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ssm.settings')
django.setup()

print(f"Django AWS_S3_CUSTOM_DOMAIN: '{settings.AWS_S3_CUSTOM_DOMAIN}'")
