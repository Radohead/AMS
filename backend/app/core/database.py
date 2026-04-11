"""
数据库连接管理
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from starlette.requests import Request
from app.core.config import settings

# 根据数据库类型选择连接方式
if settings.DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False}  # SQLite特定配置
    )
else:
    engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db(request: Request = None):
    """获取数据库会话，并注入到 request.state 供中间件共享"""
    db = SessionLocal()
    try:
        # 注入到 request.state，使中间件可复用同一 session
        if request is not None:
            request.state.db = db
        yield db
    finally:
        db.close()
