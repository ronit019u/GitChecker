import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.gitchecker.database.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, nullable=False)
    github_id = Column(Integer, unique=True, nullable=False, index=True)
    avatar_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    histories = relationship(
        "History", back_populates="user", cascade="all, delete-orphan"
    )


class History(Base):
    __tablename__ = "history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    repo_url = Column(String, nullable=False)
    task_description = Column(Text)
    planner_response = Column(Text)
    coder_response = Column(Text)
    file_path = Column(String)
    detected_language = Column(String)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="histories")
