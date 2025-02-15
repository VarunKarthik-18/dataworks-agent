# app/api.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.tasks import execute_task  # ✅ Only this import (No circular dependencies)

router = APIRouter()

class TaskRequest(BaseModel):
    task: str

class EmbeddingRequest(BaseModel):
    sentences: list[str]

@router.post("/run")
async def run_task(request: TaskRequest):
    """Receives a task request and executes it."""
    try:
        result = execute_task(request.task)
        return {"message": "Task executed successfully", "result": result}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
