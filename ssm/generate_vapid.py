
from pywebpush import WebPusher

# Generate VAPID keys
private_key = WebPusher.generate_vapid_keys()
print(f"VAPID_PRIVATE_KEY: {private_key['privateKey']}")
print(f"VAPID_PUBLIC_KEY: {private_key['publicKey']}")
