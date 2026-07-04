import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
  
TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
  db = TestingSessionLocal()
  try:
    yield db
  finally:
    db.close()
    
app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def setup_db():
  Base.metadata.create_all(bind=engine)
  yield
  Base.metadata.drop_all(bind=engine)

client = TestClient(app)

def test_create_note():
  response = client.post("/notes", json={"title":"hej", "content": "världen"})
  assert response.status_code == 201
  assert response.json()["title"] == "hej"
  
def test_get_note():
    create_response = client.post("/notes", json={"title": "hej", "content":"världen"})
    note_id = create_response.json()["id"]

    response = client.get(f"/notes/{note_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "hej"
    
def test_delete_note():
  create_response = client.post("/notes", json={"title": "hej", "content":"världen"})
  note_id = create_response.json()["id"]
  
  response = client.delete(f"/notes/{note_id}")
  assert response.status_code == 204
  
  
def test_update_note():
  create_response = client.post("/notes", json={"title": "hej", "content":"världen"})
  note_id = create_response.json()["id"]
  response = client.put(f"/notes/{note_id}", json={"title": "hoola", "content": "baloola"})
  assert response.status_code == 200
  assert response.json()["title"] == "hoola"
  
  