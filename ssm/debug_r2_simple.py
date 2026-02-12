
import os
from dotenv import load_dotenv

# Try loading .env explicitly
load_dotenv()

r2_public = os.getenv('R2_PUBLIC_URL')
r2_endpoint = os.getenv('R2_ENDPOINT_URL')

print(f"R2_PUBLIC_URL: '{r2_public}'")
print(f"R2_ENDPOINT_URL: '{r2_endpoint}'")
