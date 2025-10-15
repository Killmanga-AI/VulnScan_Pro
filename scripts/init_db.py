"""
Initialize database with all tables
"""
import sys
import os

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.core.database import Base, engine, SessionLocal, User


def init_database():
    """Create all tables and add test data"""
    print("🗄️ Creating database tables...")

    # This creates ALL tables (User, Scan, Vulnerability)
    Base.metadata.create_all(bind=engine)
    print(" Database tables created successfully!")

    # Add a test user if none exists
    db = SessionLocal()
    try:
        test_user = db.query(User).filter(User.email == "test@example.com").first()
        if not test_user:
            test_user = User(
                email="test@example.com",
                full_name="Test User",
                hashed_password="test123",  # Insecure - we'll fix later
                scan_credits=5
            )
            db.add(test_user)
            db.commit()
            print(" Test user created:")
            print(f"   Email: test@example.com")
            print(f"   Password: test123")
            print(f"   Scan credits: 5")
        else:
            print(" Test user already exists")

        # Show user count
        user_count = db.query(User).count()
        print(f" Total users in database: {user_count}")

    except Exception as e:
        print(f" Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_database()
