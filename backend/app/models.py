from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, nullable=True)
    cefr_level = Column(String, default="A1")
    created_at = Column(DateTime, default=datetime.utcnow)

    vocabulary_items = relationship("VocabularyItem", back_populates="user")
    test_records = relationship("TestRecord", back_populates="user")
    video_processes = relationship("VideoProcess", back_populates="user")


class VocabularyLevel(Base):
    __tablename__ = "vocabulary_levels"

    word = Column(String, primary_key=True)
    level = Column(String, nullable=False)  # A1/A2/B1/B2/C1/C2
    meaning = Column(Text, nullable=True)
    phonetic = Column(String, nullable=True)
    example = Column(Text, nullable=True)


class VocabularyItem(Base):
    __tablename__ = "vocabulary_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.id"))
    word = Column(String, nullable=False)
    meaning = Column(Text, nullable=True)
    phonetic = Column(String, nullable=True)
    example_sentence = Column(Text, nullable=True)
    source_video = Column(String, nullable=True)
    source_timestamp = Column(Float, nullable=True)
    cefr_level = Column(String, nullable=True)
    review_count = Column(Integer, default=0)
    next_review_date = Column(DateTime, nullable=True)
    added_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="vocabulary_items")

    # SQLite 特有的 autoincrement 配置，PostgreSQL 中不需要
    # __table_args__ 在 PostgreSQL 中会导致错误，所以注释掉
    # __table_args__ = (
    #     {'sqlite_autoincrement': True}
    # )


class VideoProcess(Base):
    __tablename__ = "video_processes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.id"))
    video_url = Column(String, nullable=True)
    video_path = Column(String, nullable=True)
    audio_path = Column(String, nullable=True)  # 音频文件路径
    status = Column(String, default="pending")  # pending/downloading_audio/processing_audio/downloading_video/completed/failed
    subtitle_data = Column(Text, nullable=True)  # JSON format
    error_message = Column(Text, nullable=True)  # Error message if processing failed
    current_step = Column(Integer, default=0)  # Current processing step
    total_steps = Column(Integer, default=5)  # Total number of steps
    step_name = Column(String, nullable=True)  # Current step name
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 最后更新时间
    completed_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="video_processes")

    # __table_args__ = (
    #     {'sqlite_autoincrement': True}
    # )


class TestRecord(Base):
    __tablename__ = "test_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.id"))
    test_type = Column(String)  # vocabulary/adaptive
    result_level = Column(String, nullable=True)
    estimated_vocab_size = Column(Integer, nullable=True)
    answers = Column(Text, nullable=True)  # JSON format
    taken_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="test_records")

    # __table_args__ = (
    #     {'sqlite_autoincrement': True}
    # )
