import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.database.session import Base

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False, default="Demo User")
    email = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    scans = relationship("Scan", back_populates="user", cascade="all, delete-orphan")
    selected_projects = relationship("SelectedProject", back_populates="user", cascade="all, delete-orphan")

class Scan(Base):
    __tablename__ = "scans"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    image_reference = Column(String(255), nullable=True)
    status = Column(String(50), default="completed")
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="scans")
    detections = relationship("Detection", back_populates="scan", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="scan", cascade="all, delete-orphan")
    selected_projects = relationship("SelectedProject", back_populates="scan", cascade="all, delete-orphan")

class Detection(Base):
    __tablename__ = "detections"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    scan_id = Column(String(36), ForeignKey("scans.id"), nullable=False)
    object_name = Column(String(100), nullable=False)
    confidence = Column(Float, nullable=True)
    bounding_box = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    scan = relationship("Scan", back_populates="detections")

class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    scan_id = Column(String(36), ForeignKey("scans.id"), nullable=False)
    project_id = Column(String(100), nullable=False)
    score = Column(Float, nullable=False)
    rank = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    scan = relationship("Scan", back_populates="recommendations")

class SelectedProject(Base):
    __tablename__ = "selected_projects"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    scan_id = Column(String(36), ForeignKey("scans.id"), nullable=True)
    project_id = Column(String(100), nullable=False)
    status = Column(String(50), default="in_progress") # selected, in_progress, completed
    selected_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="selected_projects")
    scan = relationship("Scan", back_populates="selected_projects")
    personalized_guides = relationship("PersonalizedGuide", back_populates="selected_project", cascade="all, delete-orphan")
    completions = relationship("ProjectCompletion", back_populates="selected_project", cascade="all, delete-orphan")
    chat_sessions = relationship("ChatSession", back_populates="selected_project", cascade="all, delete-orphan")

class PersonalizedGuide(Base):
    __tablename__ = "personalized_guides"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    selected_project_id = Column(String(36), ForeignKey("selected_projects.id"), nullable=False)
    guide_content = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    selected_project = relationship("SelectedProject", back_populates="personalized_guides")

class ProjectCompletion(Base):
    __tablename__ = "project_completions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    selected_project_id = Column(String(36), ForeignKey("selected_projects.id"), nullable=False)
    project_id = Column(String(100), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    completed_at = Column(DateTime, default=datetime.utcnow)

    selected_project = relationship("SelectedProject", back_populates="completions")

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    selected_project_id = Column(String(36), ForeignKey("selected_projects.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    selected_project = relationship("SelectedProject", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

class ChatMessage(BaseModel if False else Base):
    __tablename__ = "chat_messages"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(String(20), nullable=False) # user, assistant
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("ChatSession", back_populates="messages")
