"""Mints a short-lived access token for local testing without the mobile app.

Only works when the API runs with SUPABASE_JWT_SECRET set (HS256). Use the same secret here.
    SUPABASE_JWT_SECRET=dev-secret python scripts/dev_token.py you@example.com
Then:  curl -H "Authorization: Bearer <token>" http://localhost:8000/v1/me
"""
import os
import sys
import time
import uuid

import jwt

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.config import settings  # noqa: E402

email = sys.argv[1] if len(sys.argv) > 1 else "dev@example.com"
if not settings.supabase_jwt_secret:
    sys.exit("Set SUPABASE_JWT_SECRET (in .env or the shell) first.")
uid = uuid.uuid5(uuid.NAMESPACE_URL, f"skindex-dev:{email}")  # same email -> same user every time
now = int(time.time())
claims = {"sub": str(uid), "email": email, "role": "authenticated", "aud": settings.jwt_audience,
          "iat": now, "exp": now + 3600 * 8, "user_metadata": {"display_name": email.split("@")[0]}}
if settings.supabase_url:
    claims["iss"] = f"{settings.supabase_url}/auth/v1"
print(jwt.encode(claims, settings.supabase_jwt_secret, algorithm="HS256"))
