"""
数据库操作模块 - SQLite版本
"""
import sqlite3
from typing import List, Optional
from contextlib import contextmanager
import os

# 数据库路径
DB_DIR = os.path.join(os.path.dirname(__file__), 'data')
DB_PATH = os.path.join(DB_DIR, 'students.db')
os.makedirs(DB_DIR, exist_ok=True)


@contextmanager
def get_connection():
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        yield conn
    except Exception as e:
        print(f"数据库错误: {e}")
        raise
    finally:
        if conn:
            conn.close()


def init_database():
    create_students_sql = """
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT NOT NULL,
        name TEXT NOT NULL,
        gender TEXT NOT NULL,
        age INTEGER NOT NULL,
        major TEXT NOT NULL,
        score REAL NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """

    create_notes_sql = """
    CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT,
        color TEXT DEFAULT 'yellow',
        is_pinned INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(create_students_sql)
            cursor.execute(create_notes_sql)
            conn.commit()

            # 插入示例数据
            cursor.execute("SELECT COUNT(*) FROM students")
            if cursor.fetchone()[0] == 0:
                students = [
                    ('2024001', '张三', '男', 20, '计算机科学', 95),
                    ('2024002', '李四', '女', 19, '软件工程', 88),
                    ('2024003', '王五', '男', 21, '人工智能', 92),
                ]
                cursor.executemany(
                    "INSERT INTO students (student_id, name, gender, age, major, score) VALUES (?, ?, ?, ?, ?, ?)",
                    students
                )
                conn.commit()

            print("✅ 数据库初始化成功！")
    except Exception as e:
        print(f"❌ 初始化失败: {e}")


class StudentDB:
    @staticmethod
    def get_all() -> List[dict]:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM students ORDER BY id DESC")
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def get_by_id(student_id: int) -> Optional[dict]:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM students WHERE id = ?", (student_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    @staticmethod
    def create(data: dict) -> dict:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO students (student_id, name, gender, age, major, score) VALUES (?, ?, ?, ?, ?, ?)",
                (data['student_id'], data['name'], data['gender'], data['age'], data['major'], data['score'])
            )
            conn.commit()
            return StudentDB.get_by_id(cursor.lastrowid)

    @staticmethod
    def update(student_id: int, data: dict) -> Optional[dict]:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE students SET student_id=?, name=?, gender=?, age=?, major=?, score=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
                (data['student_id'], data['name'], data['gender'], data['age'], data['major'], data['score'], student_id)
            )
            conn.commit()
            return StudentDB.get_by_id(student_id)

    @staticmethod
    def delete(student_id: int) -> bool:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
            conn.commit()
            return cursor.rowcount > 0


class NoteDB:
    @staticmethod
    def get_all() -> List[dict]:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM notes ORDER BY is_pinned DESC, id DESC")
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def get_by_id(note_id: int) -> Optional[dict]:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    @staticmethod
    def create(data: dict) -> dict:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO notes (title, content, color, is_pinned) VALUES (?, ?, ?, ?)",
                (data.get('title', '新便签'), data.get('content', ''), data.get('color', 'yellow'), data.get('is_pinned', 0))
            )
            conn.commit()
            return NoteDB.get_by_id(cursor.lastrowid)

    @staticmethod
    def update(note_id: int, data: dict) -> Optional[dict]:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE notes SET title=?, content=?, color=?, is_pinned=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
                (data.get('title'), data.get('content'), data.get('color'), data.get('is_pinned', 0), note_id)
            )
            conn.commit()
            return NoteDB.get_by_id(note_id)

    @staticmethod
    def delete(note_id: int) -> bool:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def toggle_pin(note_id: int) -> Optional[dict]:
        note = NoteDB.get_by_id(note_id)
        if note:
            new_pin = 0 if note['is_pinned'] else 1
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE notes SET is_pinned=? WHERE id=?", (new_pin, note_id))
                conn.commit()
            return NoteDB.get_by_id(note_id)
        return None