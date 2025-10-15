import sqlite3
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey,Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()

SQLALCHEMY_DATABASE_URL = "sqlite:///./vulnscan.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL,connect_args={'check_same_thread': False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True,index=True)
    target_url = Column(String)
    status = Column(String, default='pending')
    user_id = Column(Integer, ForeignKey('users.id'))
    vulnerabilities_found = Column(Integer, default=0)
    risk_score = Column(Float, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Scan(Base):
    __tablename__ = 'scans'
    id = Column(Integer, primary_key=True,index=True)
    target_url = Column(String)
    status = Column(String, default='pending')
    user_id = Column(Integer, ForeignKey('users.id'))
    vulnerabilities_found = Column(Integer, default=0)
    risk_score = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

class Vulnerability(Base):
    __tablename__ = 'vulnerabilities'
    id = Column(Integer, primary_key=True,index=True)
    scan_id = Column(Integer, ForeignKey('scans.id'))
    vulnerability_type = Column(String)
    severity = Column(String)
    description = Column(Text)
    location = Column(String)
    cvss_score = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    scan = relationship("Scan", back_populates="vulnerabilities")
