from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

Base = declarative_base()

class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True)
    serial = Column(String, unique=True)
    imei = Column(String)
    model = Column(String)
    chipset = Column(String)
    mode = Column(String)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Firmware(Base):
    __tablename__ = "firmwares"

    id = Column(Integer, primary_key=True)
    model = Column(String)          # e.g., "Pixel 5"
    chipset = Column(String)        # e.g., "sm7250"
    version = Column(String)        # e.g., "Android 13"
    url = Column(String)            # direct download URL
    sha256 = Column(String)         # expected SHA-256 checksum
    source = Column(String)         # official source name
    file_path = Column(String)      # local path after download
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True)
    device_id = Column(Integer)
    firmware_id = Column(Integer)
    technician = Column(String)
    status = Column(String)         # queued, in_progress, success, failed
    logs = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class Outcome(Base):
    __tablename__ = "outcomes"

    id = Column(Integer, primary_key=True)
    job_id = Column(Integer)
    success = Column(Boolean)
    error_log = Column(Text)
    duration_secs = Column(Integer)
    ai_notes = Column(Text)
