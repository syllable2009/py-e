from .db_service import init_db, get_session, ORMService
from models.user import User

# 初始化（应用启动时调用一次）
init_db()

# 示例：增删改查 + 分页
def demo():
    with get_session() as session:
        # 创建
        user = User(name="Alice", email="alice@example.com")
        ORMService.create(session, user)
        print(f"Created user ID: {user.id}")

        # 批量创建
        users = [User(name=f"User{i}", email=f"user{i}@ex.com") for i in range(2, 6)]
        ORMService.bulk_create(session, users)

        # 查询单条
        u = ORMService.get_by_id(session, User, 1)
        print("Found:", u.to_dict() if u else None)

        # 分页查询
        query = session.query(User).filter(User.name.like("User%"))
        result = ORMService.paginate(session, query, page=1, size=3)
        print("Page 1 items:", [u.to_dict() for u in result["items"]])
        print("Total:", result["total"])

        # 更新
        ORMService.update_by_id(session, User, 1, name="Alice Updated")

        # 删除
        ORMService.delete_by_id(session, User, 2)

if __name__ == "__main__":
    demo()