"""
学生管理系统 - FastAPI后端（含便签功能）
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from database import StudentDB, NoteDB, init_database

app = FastAPI(
    title="🎓 学生管理系统 API",
    description="包含学生管理和便签功能",
    version="2.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== 数据模型 ====================

# 学生模型
class StudentBase(BaseModel):
    student_id: str
    name: str
    gender: str
    age: int = Field(ge=16, le=50)
    major: str
    score: float = Field(ge=0, le=100)

class StudentCreate(StudentBase):
    pass

class StudentUpdate(StudentBase):
    pass

# 便签模型
class NoteBase(BaseModel):
    title: str = Field(max_length=100)
    content: Optional[str] = ""
    color: str = "yellow"
    is_pinned: int = 0

class NoteCreate(NoteBase):
    pass

class NoteUpdate(NoteBase):
    pass


# ==================== 启动事件 ====================

@app.on_event("startup")
async def startup():
    print("🚀 正在启动学生管理系统...")
    try:
        init_database()
        print("✅ 系统启动成功！")
    except Exception as e:
        print(f"⚠️ 启动警告: {e}")


# ==================== 学生API ====================

@app.get("/api/students", tags=["学生管理"])
async def get_students():
    """获取所有学生"""
    try:
        return StudentDB.get_all()
    except:
        return get_mock_students()

@app.post("/api/students", tags=["学生管理"])
async def create_student(student: StudentCreate):
    """创建学生"""
    try:
        return StudentDB.create(student.dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/students/{student_id}", tags=["学生管理"])
async def update_student(student_id: int, student: StudentUpdate):
    """更新学生"""
    result = StudentDB.update(student_id, student.dict())
    if not result:
        raise HTTPException(status_code=404, detail="学生不存在")
    return result

@app.delete("/api/students/{student_id}", tags=["学生管理"])
async def delete_student(student_id: int):
    """删除学生"""
    if StudentDB.delete(student_id):
        return {"success": True, "message": "删除成功"}
    raise HTTPException(status_code=404, detail="学生不存在")


# ==================== 便签API ====================

@app.get("/api/notes", tags=["便签管理"])
async def get_notes(search: Optional[str] = Query(None)):
    """获取所有便签"""
    try:
        if search:
            return NoteDB.search(search)
        return NoteDB.get_all()
    except:
        return get_mock_notes()

@app.get("/api/notes/{note_id}", tags=["便签管理"])
async def get_note(note_id: int):
    """获取单个便签"""
    note = NoteDB.get_by_id(note_id)
    if not note:
        raise HTTPException(status_code=404, detail="便签不存在")
    return note

@app.post("/api/notes", tags=["便签管理"])
async def create_note(note: NoteCreate):
    """创建便签"""
    try:
        return NoteDB.create(note.dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/notes/{note_id}", tags=["便签管理"])
async def update_note(note_id: int, note: NoteUpdate):
    """更新便签"""
    result = NoteDB.update(note_id, note.dict())
    if not result:
        raise HTTPException(status_code=404, detail="便签不存在")
    return result

@app.delete("/api/notes/{note_id}", tags=["便签管理"])
async def delete_note(note_id: int):
    """删除便签"""
    if NoteDB.delete(note_id):
        return {"success": True, "message": "删除成功"}
    raise HTTPException(status_code=404, detail="便签不存在")

@app.post("/api/notes/{note_id}/toggle-pin", tags=["便签管理"])
async def toggle_pin_note(note_id: int):
    """切换便签置顶状态"""
    result = NoteDB.toggle_pin(note_id)
    if not result:
        raise HTTPException(status_code=404, detail="便签不存在")
    return result


# ==================== 模拟数据 ====================

def get_mock_students():
    return [
        {"id": 1, "student_id": "2024001", "name": "张三", "gender": "男", "age": 20, "major": "计算机科学", "score": 95},
        {"id": 2, "student_id": "2024002", "name": "李四", "gender": "女", "age": 19, "major": "软件工程", "score": 88},
    ]

def get_mock_notes():
    return [
        {"id": 1, "title": "欢迎使用", "content": "这是便签示例", "color": "yellow", "is_pinned": 1},
        {"id": 2, "title": "待办事项", "content": "完成作业", "color": "blue", "is_pinned": 0},
    ]


# ==================== 主程序 ====================

if __name__ == "__main__":
    import uvicorn
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║    🎓 学生管理系统 v2.0 (含便签功能)                        ║
    ║    后端地址: http://localhost:8000                        ║
    ║    API文档:  http://localhost:8000/docs                   ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)