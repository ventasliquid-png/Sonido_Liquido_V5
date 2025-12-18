import sys
import os

# Set up module path to include project root
sys.path.append(os.getcwd())

from backend.core.database import SessionLocal
from backend.auth import service
from backend.auth import models

def debug_auth():
    print("--- Debugging Auth ---")
    db = SessionLocal()
    try:
        # 1. Check User exists
        print("1. Checking User 'admin'...")
        user = service.get_usuario_by_username(db, "admin")
        if not user:
            print("❌ User 'admin' NOT FOUND in DB.")
            return
        print(f"✅ Found User: {user.username} (ID: {user.id})")
        print(f"   Hashed Pwd: {user.hashed_password} (Type: {type(user.hashed_password)})")

        # 2. Check Password Verification
        print("\n2. Verifying Password 'admin'...")
        try:
            is_valid = service.verify_password("admin", user.hashed_password)
            if is_valid:
                print("✅ Password verification SUCCESS.")
            else:
                print("❌ Password verification FAILED (False returned).")
        except Exception as e:
            print(f"❌ Password verification CRASHED: {e}")

        # 3. Check Authenticate User Flow
        print("\n3. Testing authenticate_user()...")
        try:
            auth_user = service.authenticate_user(db, "admin", "admin")
            if auth_user:
                print("✅ authenticate_user() SUCCESS.")
            else:
                print("❌ authenticate_user() RETURNED FALSE.")
        except Exception as e:
            print(f"❌ authenticate_user() CRASHED: {e}")

        # 4. Check Token Generation
        print("\n4. Testing create_access_token()...")
        try:
            token = service.create_access_token(data={"sub": "admin"})
            print(f"✅ Token Gen SUCCESS: {token[:20]}...")
        except Exception as e:
            print(f"❌ Token Gen CRASHED: {e}")
            import traceback
            traceback.print_exc()

    except Exception as e:
        print(f"❌ General Debug Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    debug_auth()
