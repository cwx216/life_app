import sqlite3
import os
import sys
from datetime import datetime

# 全局统一数据库路径
if getattr(sys, 'frozen', False):
    base_path = os.path.dirname(sys.executable)
else:
    base_path = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(base_path, "lifedata.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # 数据记录表
    c.execute('''
    CREATE TABLE IF NOT EXISTS personal_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT,
        value REAL,
        remark TEXT,
        create_time TEXT
    )
    ''')
    # 智能建议表
    c.execute('''
    CREATE TABLE IF NOT EXISTS smart_suggestion (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        content TEXT,
        reason TEXT,
        type TEXT,
        create_time TEXT
    )
    ''')
    conn.commit()
    conn.close()
    print("✅ 数据库初始化成功！")

def add_data(data_type, value, remark=""):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        c.execute('''
        INSERT INTO personal_data (type, value, remark, create_time)
        VALUES (?, ?, ?, ?)
        ''', (data_type, value, remark, now))
        conn.commit()
        print(f"✅ 写入成功：{data_type} {value} {remark}")
    except Exception as e:
        print(f"❌ 写入失败：{e}")
        conn.rollback()
    finally:
        conn.close()

# 给功能2用：今日所有数据
def query_today_all_data():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    c.execute('''
        SELECT type, SUM(value)
        FROM personal_data
        WHERE DATE(create_time) = ?
        GROUP BY type
    ''', (today,))
    rows = c.fetchall()
    conn.close()
    return rows

# 给功能4用：今日消费分类汇总
def query_today_cost_data():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    c.execute('''
        SELECT remark, SUM(value)
        FROM personal_data
        WHERE type='cost' AND DATE(create_time) = ?
        GROUP BY remark
    ''', (today,))
    rows = c.fetchall()
    conn.close()
    return rows

# ========== 新增：智能建议相关接口 ==========
# 添加一条智能建议
def add_suggestion(title, content, reason, type_="日常"):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        c.execute('''
        INSERT INTO smart_suggestion (title, content, reason, type, create_time)
        VALUES (?, ?, ?, ?, ?)
        ''', (title, content, reason, type_, now))
        conn.commit()
        print(f"💡 智能建议已添加：{title}")
    except Exception as e:
        print(f"❌ 添加建议失败：{e}")
        conn.rollback()
    finally:
        conn.close()

# 查询所有智能建议（倒序，最新在前）
def query_all_suggestions():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        SELECT id, title, content, reason, type, create_time
        FROM smart_suggestion
        ORDER BY create_time DESC
    ''')
    rows = c.fetchall()
    conn.close()
    return rows