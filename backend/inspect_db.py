"""
文件名: inspect_db.py
作用: 这是一个数据库检查工具，用于检查和记录数据库的结构和内容。
      它会生成一个带时间戳的日志文件，记录：
      1. 数据库中所有表的结构信息（表名、列、主键、外键等）
      2. 各个表中的实际数据内容
      日志文件保存在logs目录下，便于后续查看和分析。
"""

# 导入所需的标准库
import os  # 用于文件和目录操作
from datetime import datetime  # 用于处理日期和时间

# 导入SQLAlchemy相关组件
from sqlalchemy import inspect  # 用于检查数据库结构
from app.database import engine, SessionLocal  # 导入数据库引擎和会话工厂
from app.models import User, Exercise, Question  # 导入数据模型

def write_database_info(file):
    """
    将数据库的结构信息写入指定文件
    
    Args:
        file: 要写入的文件对象
    """
    # 创建数据库检查器实例
    inspector = inspect(engine)
    
    # 写入表信息的标题
    file.write("\n=== 数据库中的表 ===\n")
    
    # 遍历所有表
    for table_name in inspector.get_table_names():
        # 写入表名
        file.write(f"\n表名: {table_name}\n")
        
        # 写入表的列信息
        file.write("列信息:\n")
        for column in inspector.get_columns(table_name):
            file.write(f"  - {column['name']}: {column['type']}\n")
            
        # 写入表的主键信息
        pk = inspector.get_pk_constraint(table_name)
        file.write(f"主键: {pk['constrained_columns']}\n")
        
        # 写入表的外键信息
        fks = inspector.get_foreign_keys(table_name)
        if fks:  # 如果存在外键
            file.write("外键:\n")
            for fk in fks:
                file.write(f"  - {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}\n")

def write_table_data(file):
    """
    将表中的实际数据写入指定文件
    
    Args:
        file: 要写入的文件对象
    """
    # 创建数据库会话
    db = SessionLocal()
    try:
        # 写入用户表数据
        file.write("\n=== 用户数据 ===\n")
        users = db.query(User).all()  # 查询所有用户
        for user in users:
            file.write(f"用户ID: {user.id}\n")
            file.write(f"邮箱: {user.email}\n")
            file.write(f"用户名: {user.username}\n")
            file.write("---\n")  # 分隔符

        # 写入练习表数据
        file.write("\n=== 练习数据 ===\n")
        exercises = db.query(Exercise).all()  # 查询所有练习
        for exercise in exercises:
            file.write(f"练习ID: {exercise.id}\n")
            file.write(f"用户ID: {exercise.user_id}\n")
            file.write(f"难度: {exercise.difficulty}\n")
            file.write(f"数值范围: {exercise.number_range}\n")
            file.write(f"运算符: {exercise.operator_types}\n")
            file.write(f"得分: {exercise.final_score}\n")
            file.write(f"总用时: {exercise.total_time}秒\n")
            file.write(f"创建时间: {exercise.created_at}\n")
            file.write("---\n")  # 分隔符

        # 写入题目表数据
        file.write("\n=== 题目数据 ===\n")
        questions = db.query(Question).all()  # 查询所有题目
        for question in questions:
            file.write(f"题目ID: {question.id}\n")
            file.write(f"练习ID: {question.exercise_id}\n")
            file.write(f"内容: {question.content}\n")
            file.write(f"正确答案: {question.correct_answer}\n")
            file.write(f"用户答案: {question.user_answer}\n")
            file.write(f"用时: {question.time_spent}秒\n")
            file.write(f"是否正确: {question.is_correct}\n")
            file.write("---\n")  # 分隔符

    finally:
        # 确保会话被关闭
        db.close()

if __name__ == "__main__":
    # 创建logs目录（如果不存在）
    os.makedirs('logs', exist_ok=True)
    
    # 生成带时间戳的文件名，格式：db_info_年月日_时分秒.txt
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'logs/db_info_{timestamp}.txt'
    
    # 打开文件并写入数据
    with open(filename, 'w', encoding='utf-8') as f:
        # 写入文件头部信息
        f.write(f"数据库检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 50 + "\n")  # 分隔线
        
        # 依次写入数据库结构和数据内容
        write_database_info(f)
        write_table_data(f)
        
    # 输出成功信息
    print(f"数据库信息已写入文件: {filename}")