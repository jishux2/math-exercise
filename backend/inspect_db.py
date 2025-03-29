import os
from datetime import datetime

from sqlalchemy import inspect
from app.database import engine, SessionLocal
from app.models import User, Exercise, Question

def write_database_info(file):
    """将数据库信息写入文件"""
    # 获取所有表的信息
    inspector = inspect(engine)
    
    file.write("\n=== 数据库中的表 ===\n")
    for table_name in inspector.get_table_names():
        file.write(f"\n表名: {table_name}\n")
        
        # 打印表的列信息
        file.write("列信息:\n")
        for column in inspector.get_columns(table_name):
            file.write(f"  - {column['name']}: {column['type']}\n")
            
        # 打印主键
        pk = inspector.get_pk_constraint(table_name)
        file.write(f"主键: {pk['constrained_columns']}\n")
        
        # 打印外键
        fks = inspector.get_foreign_keys(table_name)
        if fks:
            file.write("外键:\n")
            for fk in fks:
                file.write(f"  - {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}\n")

def write_table_data(file):
    """将表数据写入文件"""
    db = SessionLocal()
    try:
        # 查询用户数据
        file.write("\n=== 用户数据 ===\n")
        users = db.query(User).all()
        for user in users:
            file.write(f"用户ID: {user.id}\n")
            file.write(f"邮箱: {user.email}\n")
            file.write(f"用户名: {user.username}\n")
            file.write("---\n")

        # 查询练习数据
        file.write("\n=== 练习数据 ===\n")
        exercises = db.query(Exercise).all()
        for exercise in exercises:
            file.write(f"练习ID: {exercise.id}\n")
            file.write(f"用户ID: {exercise.user_id}\n")
            file.write(f"难度: {exercise.difficulty}\n")
            file.write(f"数值范围: {exercise.number_range}\n")
            file.write(f"运算符: {exercise.operator_types}\n")
            file.write(f"得分: {exercise.final_score}\n")
            file.write(f"总用时: {exercise.total_time}秒\n")
            file.write(f"创建时间: {exercise.created_at}\n")
            file.write("---\n")

        # 查询题目数据
        file.write("\n=== 题目数据 ===\n")
        questions = db.query(Question).all()
        for question in questions:
            file.write(f"题目ID: {question.id}\n")
            file.write(f"练习ID: {question.exercise_id}\n")
            file.write(f"内容: {question.content}\n")
            file.write(f"正确答案: {question.correct_answer}\n")
            file.write(f"用户答案: {question.user_answer}\n")
            file.write(f"用时: {question.time_spent}秒\n")
            file.write(f"是否正确: {question.is_correct}\n")  # 添加这行
            file.write("---\n")

    finally:
        db.close()

if __name__ == "__main__":
    # 创建输出目录（如果不存在）
    os.makedirs('logs', exist_ok=True)
    
    # 生成包含时间戳的文件名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'logs/db_info_{timestamp}.txt'
    
    # 写入文件
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"数据库检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 50 + "\n")
        
        write_database_info(f)
        write_table_data(f)
        
    print(f"数据库信息已写入文件: {filename}")