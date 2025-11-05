from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    hashed_password = Column(String)
    plan_tier = Column(String, default="free")
    scan_credits = Column(Integer, default=5)
    scans = relationship("Scan", back_populates="user")

class Scan(Base):
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    target_url = Column(String)
    result = Column(Text)

    user = relationship("User", back_populates="scans")
    vulnerabilities = relationship("Vulnerability", back_populates="scan")

class Vulnerability(Base):
    __tablename__ = "vulnerabilities"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id"))
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    scan = relationship("Scan", back_populates="vulnerabilities")
