import os
from fastapi import FastAPI
from app.api import todos

app = FastAPI(
    title="Todo API",
    description="A simple CRUD API for managing todos",
    version="1.0.0"
)

# Only create tables if not in test mode
if os.getenv("TESTING") != "1":
    from app.database import Base, engine
    Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(todos.router, prefix="/api")


@app.get("/")
def root():
    return {
        "message": "Welcome to Todo API",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
