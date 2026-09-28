from database import SessionLocal, engine
import models, auth

# Connect to DB
db = SessionLocal()

# Create Admin User
username = "farzam"
password = "password123"

# Check if exists
existing = db.query(models.User).filter(models.User.username == username).first()
if not existing:
    hashed_pw = auth.get_password_hash(password)
    user = models.User(username=username, hashed_password=hashed_pw)
    db.add(user)
    db.commit()
    print(f"✅ Created User: {username} / {password}")
else:
    print("⚠️ User already exists")

db.close()