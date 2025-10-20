from fastapi import FastAPI
from app.api import todos
from app.database import Base, engine

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Todo API",
    description="A simple CRUD API for managing todos",
    version="1.0.0"
)

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
