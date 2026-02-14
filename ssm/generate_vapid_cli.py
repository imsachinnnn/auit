
# Correct way to generate VAPID keys using pywebpush library directly if available or subprocess
import os

try:
    # Try using the command line tool installed by pywebpush
    os.system("vapid --application-server-key")
except Exception as e:
    print(f"Error: {e}")
