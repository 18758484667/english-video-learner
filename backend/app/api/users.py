from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

from ..database import get_db
from ..models import User

router = APIRouter()

# Pydantic模型
class UserCreate(BaseModel):
    username: str
    email: Optional[str] = None
    cefr_level: Optional[str] = "A1"

class UserResponse(BaseModel):
    id: str
    username: str
    email: Optional[str]
    cefr_level: str
    created_at: datetime

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    cefr_level: Optional[str] = None

@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """创建新用户"""
    # 检查用户名是否已存在
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    # 创建新用户
    db_user = User(
        id=str(uuid.uuid4()),
        username=user.username,
        email=user.email,
        cefr_level=user.cefr_level or "A1"
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: str, db: Session = Depends(get_db)):
    """获取用户信息"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: str, update_data: UserUpdate, db: Session = Depends(get_db)):
    """更新用户信息"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if update_data.cefr_level:
        user.cefr_level = update_data.cefr_level

    db.commit()
    db.refresh(user)

    return user
