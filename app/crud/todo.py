from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.todo import Todo
from app.schemas.todo import TodoCreate, TodoUpdate


def get_todo(db: Session, todo_id: int) -> Optional[Todo]:
    """Get a single todo by ID"""
    return db.query(Todo).filter(Todo.id == todo_id).first()


def get_todos(db: Session, skip: int = 0, limit: int = 100) -> List[Todo]:
    """Get all todos with pagination"""
    return db.query(Todo).offset(skip).limit(limit).all()


def create_todo(db: Session, todo: TodoCreate) -> Todo:
    """Create a new todo"""
    db_todo = Todo(**todo.model_dump())
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo


def update_todo(db: Session, todo_id: int, todo: TodoUpdate) -> Optional[Todo]:
    """Update an existing todo"""
    db_todo = get_todo(db, todo_id)
    if db_todo is None:
        return None

    update_data = todo.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_todo, field, value)

    db.commit()
    db.refresh(db_todo)
    return db_todo


def delete_todo(db: Session, todo_id: int) -> bool:
    """Delete a todo"""
    db_todo = get_todo(db, todo_id)
    if db_todo is None:
        return False

    db.delete(db_todo)
    db.commit()
    return True
