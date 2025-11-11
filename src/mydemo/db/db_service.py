import atexit
from contextlib import contextmanager
from typing import Any, Dict, List, Optional, Type, TypeVar

from sqlalchemy import create_engine, func, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

from config import DB_URL

Base = declarative_base()
T = TypeVar("T", bound=Base)

# 全局引擎和会话工厂
_engine: Optional[Engine] = None
_SessionFactory: Optional[sessionmaker] = None


def init_db():
    """初始化数据库引擎和会话工厂（单例）"""
    global _engine, _SessionFactory
    if _engine is None:
        _engine = create_engine(
            DB_URL,
            pool_size=10,  # 连接池大小
            max_overflow=20,  # 超出 pool_size 后最多创建的连接数
            pool_pre_ping=True,  # 每次获取连接前 ping 一下，避免 stale connection
            pool_recycle=3600,  # 1小时回收连接（应对 MySQL wait_timeout）
            echo=False,  # 生产环境设为 False
        )
        _SessionFactory = sessionmaker(bind=_engine)
        atexit.register(close_db)  # 注册退出清理


def close_db():
    """关闭数据库引擎"""
    global _engine
    if _engine:
        _engine.dispose()
        print("✅ Database engine disposed.")


@contextmanager
def get_session() -> Session:
    """上下文管理器：自动 commit/rollback/close"""
    if _SessionFactory is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")

    session = _SessionFactory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


# ------------------ ORM 通用 CRUD 服务 ------------------

class ORMService:
    @staticmethod
    def create(session: Session, instance: Base) -> Base:
        """插入单条记录"""
        session.add(instance)
        session.flush()  # 获取自增 ID（不提交事务）
        return instance

    @staticmethod
    def bulk_create(session: Session, instances: List[Base]) -> int:
        """批量插入（高效）"""
        session.bulk_save_objects(instances)
        return len(instances)

    @staticmethod
    def update_by_id(session: Session, model_cls: Type[T], id_: int, **kwargs) -> bool:
        """按 ID 更新"""
        result = session.query(model_cls).filter(model_cls.id == id_).update(kwargs)
        return result > 0

    @staticmethod
    def delete_by_id(session: Session, model_cls: Type[T], id_: int) -> bool:
        """按 ID 删除"""
        result = session.query(model_cls).filter(model_cls.id == id_).delete()
        return result > 0

    @staticmethod
    def get_by_id(session: Session, model_cls: Type[T], id_: int) -> Optional[T]:
        """按 ID 查询"""
        return session.query(model_cls).filter(model_cls.id == id_).first()

    @staticmethod
    def list_all(session: Session, model_cls: Type[T]) -> List[T]:
        """查询所有"""
        return session.query(model_cls).all()

    @staticmethod
    def paginate(
            session: Session,
            query,
            page: int,
            size: int
    ) -> Dict[str, Any]:
        """通用分页方法"""
        if page < 1 or size < 1:
            raise ValueError("page and size must be positive integers")

        total = query.count()
        items = query.offset((page - 1) * size).limit(size).all()

        return {
            "items": items,
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size,
        }