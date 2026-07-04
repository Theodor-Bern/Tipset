from sqlalchemy.orm import  Mapped, mapped_column
from sqlalchemy import String, Integer
from app.database import Base

class Note(Base):
    __tablename__= "notes"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String)
    content: Mapped[str] = mapped_column(String)