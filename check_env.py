#!/usr/bin/env python3
"""Quick script to check if environment variables are being loaded correctly"""

import os
from pathlib import Path

# Check if .env file exists
env_path = Path(".env")
if env_path.exists():
    print("✅ .env file found")
    
    # Read and check Google OAuth variables
    with open(env_path, 'r') as f:
        content = f.read()
        
    has_client_id = "GOOGLE_OAUTH_CLIENT_ID" in content
    has_client_secret = "GOOGLE_OAUTH_CLIENT_SECRET" in content
    has_app_base_url = "APP_BASE_URL" in content
    
    print(f"\n📋 Environment variables in .env file:")
    print(f"   GOOGLE_OAUTH_CLIENT_ID: {'✅ Found' if has_client_id else '❌ Missing'}")
    print(f"   GOOGLE_OAUTH_CLIENT_SECRET: {'✅ Found' if has_client_secret else '❌ Missing'}")
    print(f"   APP_BASE_URL: {'✅ Found' if has_app_base_url else '❌ Missing'}")
    
    # Check actual values (safely)
    for line in content.split('\n'):
        line = line.strip()
        if line.startswith('GOOGLE_OAUTH_CLIENT_ID=') and not line.startswith('#'):
            value = line.split('=', 1)[1].strip()
            if value and value != 'None':
                print(f"\n✅ GOOGLE_OAUTH_CLIENT_ID is set: {value[:30]}...")
            else:
                print(f"\n❌ GOOGLE_OAUTH_CLIENT_ID is empty or None")
            break
    else:
        print(f"\n❌ GOOGLE_OAUTH_CLIENT_ID not found in .env")
        
else:
    print("❌ .env file NOT found in current directory")
    print(f"   Current directory: {os.getcwd()}")

# Check environment variables from os
print(f"\n🔍 Environment variables from os.getenv():")
client_id_env = os.getenv("GOOGLE_OAUTH_CLIENT_ID")
client_secret_env = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET")
app_base_url_env = os.getenv("APP_BASE_URL")

print(f"   GOOGLE_OAUTH_CLIENT_ID: {client_id_env[:30] + '...' if client_id_env else 'None'}")
print(f"   GOOGLE_OAUTH_CLIENT_SECRET: {'***' if client_secret_env else 'None'}")
print(f"   APP_BASE_URL: {app_base_url_env or 'None'}")

print(f"\n💡 If .env file exists but environment variables are None:")
print(f"   1. Make sure the backend server is restarted")
print(f"   2. Check that .env file is in the root directory (where you run uvicorn)")
print(f"   3. Verify .env file doesn't have syntax errors (no spaces around =)")
