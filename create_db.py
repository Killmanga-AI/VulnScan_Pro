#!/usr/bin/env python3
import os
from app.core.database import Base, engine, SessionLocal
from app.core.models import User, Scan, Vulnerability

print("🗄️ Creating database tables...")
Base.metadata.create_all(bind=engine)
print("✅ Database tables created successfully!")

# Add a test user
db = SessionLocal()
try:
    test_user = db.query(User).filter(User.email == "test@example.com").first()
    if not test_user:
        test_user = User(
            email="test@example.com",
            full_name="Test User",
            hashed_password="test123",
            scan_credits=5
        )
        db.add(test_user)
        db.commit()
        print("✅ Test user created: test@example.com / test123")
    else:
        print("ℹ️ Test user already exists")

    user_count = db.query(User).count()
    print(f"📊 Total users in database: {user_count}")

except Exception as e:
    print(f"❌ Error: {e}")
    db.rollback()
finally:
    db.close()