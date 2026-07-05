from sqlalchemy.orm import  Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey
from app.database import Base

class Note(Base):
    __tablename__= "notes"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String)
    content: Mapped[str] = mapped_column(String)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    owner: Mapped["User | None"] = relationship(back_populates="notes")
    
class User(Base):
    __tablename__ = "users"
    id : Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True)
    password_hash: Mapped[str] 
    notes: Mapped[list["Note"]] = relationship(back_populates="owner")