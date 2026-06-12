from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI()

notes = []

class NoteCreate(BaseModel):
    title: str
    content: str

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/health")
def health():
    return {"message": "healthy"}

@app.post("/notes")
def create_note(note: NoteCreate):
    notes.append(note)
    return note

@app.get("/notes")
def list_notes():
    return notes