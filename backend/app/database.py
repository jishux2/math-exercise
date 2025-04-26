"""app/database.py
作用：配置SQLAlchemy，创建数据库引擎和会话管理器

这个文件主要完成三个任务：
1. 创建数据库引擎（管理数据库连接）
2. 创建会话工厂（用于创建数据库会话）
3. 提供获取数据库会话的依赖函数
"""

from sqlalchemy import create_engine
# create_engine：创建数据库引擎的函数
# 数据库引擎是SQLAlchemy连接数据库的核心组件
# 它负责管理数据库连接池和处理数据库操作

from sqlalchemy.ext.declarative import declarative_base
# declarative_base：创建声明性基类的函数
# 这个基类会被所有的ORM模型继承
# 它提供了将Python类映射到数据库表的功能

from sqlalchemy.orm import sessionmaker, Session
# sessionmaker：创建会话工厂的类
# Session：会话类的类型提示
# 会话(Session)是处理数据库操作的主要接口

from typing import Generator
# Generator：生成器类型的类型提示
# 用于标注get_db函数的返回类型

from .config import settings
# 导入配置模块中的设置
# 包含数据库URL等配置信息

# 创建SQLite数据库引擎
engine = create_engine(
    settings.DATABASE_URL,  # 数据库URL，从配置中获取
    connect_args={"check_same_thread": False}  # SQLite特有的设置
    # SQLite默认只允许创建它的线程访问数据库
    # 设置check_same_thread=False允许其他线程访问
    # 注意：这个设置只在SQLite中需要，其他数据库不需要
)

# 创建会话工厂
SessionLocal = sessionmaker(
    autocommit=False,  # 不自动提交事务
    # 如果设为True，每个操作都会立即提交
    # 设为False可以让我们手动控制事务
    
    autoflush=False,   # 不自动刷新
    # 如果设为True，每个查询前都会自动刷新session
    # 设为False可以让我们手动控制刷新时机
    
    bind=engine        # 绑定到我们创建的引擎
    # 告诉会话工厂使用哪个数据库引擎
)

# 创建声明性基类
Base = declarative_base()
# 这个基类会被所有的ORM模型继承
# 例如：class User(Base): ...
# 它提供了：
# 1. __tablename__属性定义表名
# 2. 将类属性映射到表列的功能
# 3. 提供了一些通用的数据库操作方法

def get_db() -> Generator[Session, None, None]:
    """创建数据库会话的依赖函数
    
    这是一个生成器函数，用于：
    1. 创建数据库会话
    2. 在请求处理完成后自动关闭会话
    3. 作为FastAPI的依赖项使用
    
    使用方式：
    @app.get("/users/")
    def get_users(db: Session = Depends(get_db)):
        return db.query(User).all()
    
    Returns:
        Generator[Session, None, None]: 数据库会话生成器
        - Session: 生成的类型
        - None: send()方法的参数类型（这里不使用）
        - None: return语句的类型（这里不使用）
    """
    db = SessionLocal()  # 创建新的数据库会话
    try:
        yield db  # 暂时返回会话给调用者使用
        # yield使这个函数成为生成器
        # FastAPI会在请求处理完成后自动恢复这个函数的执行
    finally:
        # finally确保无论如何都会关闭会话
        # 即使发生异常也会执行这个代码块
        db.close()  # 关闭数据库会话