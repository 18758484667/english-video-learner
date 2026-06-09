from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
import os

# 优先使用环境变量 DATABASE_URL（Render 等平台会自动提供）
# 本地开发回退到 SQLite
DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    # PostgreSQL 或其他外部数据库
    # Render 提供的 URL 以 postgres:// 开头，SQLAlchemy 需要 postgresql://
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    engine = create_engine(DATABASE_URL, poolclass=NullPool)
else:
    # 本地开发使用 SQLite
    DATABASE_URL = "sqlite:///./data/english_learner.db"
    # 确保data目录存在
    os.makedirs(os.path.dirname(DATABASE_URL.replace("sqlite:///", "")), exist_ok=True)
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
