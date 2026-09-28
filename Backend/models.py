from sqlalchemy import Column, Integer, String, Float, Boolean
from database import Base

# 1. System Stats (Counters)
class SystemStats(Base):
    __tablename__ = "system_stats"
    id = Column(Integer, primary_key=True, index=True)
    total_requests = Column(Integer, default=0)
    blocked_requests = Column(Integer, default=0)
    allowed_requests = Column(Integer, default=0)

# 2. Security Logs (Recent Events)
class SecurityLog(Base):
    __tablename__ = "security_logs"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(String)
    attack_type = Column(String)
    status = Column(String)
    latency = Column(String)
    path = Column(String)

# 3. User Table (For Login)
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="admin")