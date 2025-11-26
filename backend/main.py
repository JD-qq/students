from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from database import StudentDB, NoteDB, init_database

app = FastAPI(title="学生管理系统API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Student(BaseModel):
    student_id: str
    name: str
    gender: str
    age: int
    major: str
    score: float


class Note(BaseModel):
    title: str
    content: Optional[str] = ""
    color: Optional[str] = "yellow"
    is_pinned: Optional[int] = 0


@app.on_event("startup")
async def startup():
    init_database()


@app.get("/")
async def root():
    return {"message": "学生管理系统API运行中"}


@app.get("/api/students")
async def get_students():
    return StudentDB.get_all()


@app.post("/api/students")
async def create_student(student: Student):
    return StudentDB.create(student.dict())


@app.put("/api/students/{student_id}")
async def update_student(student_id: int, student: Student):
    result = StudentDB.update(student_id, student.dict())
    if not result:
        raise HTTPException(status_code=404, detail="学生不存在")
    return result


@app.delete("/api/students/{student_id}")
async def delete_student(student_id: int):
    if StudentDB.delete(student_id):
        return {"success": True}
    raise HTTPException(status_code=404, detail="学生不存在")


@app.get("/api/notes")
async def get_notes():
    return NoteDB.get_all()


@app.post("/api/notes")
async def create_note(note: Note):
    return NoteDB.create(note.dict())


@app.put("/api/notes/{note_id}")
async def update_note(note_id: int, note: Note):
    result = NoteDB.update(note_id, note.dict())
    if not result:
        raise HTTPException(status_code=404, detail="便签不存在")
    return result


@app.delete("/api/notes/{note_id}")
async def delete_note(note_id: int):
    if NoteDB.delete(note_id):
        return {"success": True}
    raise HTTPException(status_code=404, detail="便签不存在")


@app.post("/api/notes/{note_id}/toggle-pin")
async def toggle_pin(note_id: int):
    result = NoteDB.toggle_pin(note_id)
    if not result:
        raise HTTPException(status_code=404, detail="便签不存在")
    return result