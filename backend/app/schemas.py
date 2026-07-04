from pydantic import BaseModel, Field

class NoteCreate(BaseModel):
    title: str = Field(min_length=1, max_length=30)
    content : str = Field(min_length=1, max_length=1000)


class NoteOut(BaseModel):
    id: int
    title: str
    content: str
    model_config = {"from_attributes": True}