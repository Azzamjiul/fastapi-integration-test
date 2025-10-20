from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.todo import TodoCreate, TodoUpdate, TodoResponse
from app.crud import todo as crud_todo

router = APIRouter(
    prefix="/todos",
    tags=["todos"]
)


@router.post("/", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
def create_todo(
    todo: TodoCreate,
    db: Session = Depends(get_db)
):
    """Create a new todo"""
    return crud_todo.create_todo(db=db, todo=todo)


@router.get("/", response_model=List[TodoResponse])
def read_todos(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all todos"""
    todos = crud_todo.get_todos(db, skip=skip, limit=limit)
    return todos


@router.get("/{todo_id}", response_model=TodoResponse)
def read_todo(
    todo_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific todo by ID"""
    db_todo = crud_todo.get_todo(db, todo_id=todo_id)
    if db_todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )
    return db_todo


@router.put("/{todo_id}", response_model=TodoResponse)
def update_todo(
    todo_id: int,
    todo: TodoUpdate,
    db: Session = Depends(get_db)
):
    """Update a todo"""
    db_todo = crud_todo.update_todo(db, todo_id=todo_id, todo=todo)
    if db_todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )
    return db_todo


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(
    todo_id: int,
    db: Session = Depends(get_db)
):
    """Delete a todo"""
    success = crud_todo.delete_todo(db, todo_id=todo_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )
    return None
