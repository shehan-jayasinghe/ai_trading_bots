from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependencies import get_postgres_db
from app.middleware.auth import get_current_user
from app.models.user_model import User
from app.schemas.workflow_schema import WorkflowCreate, WorkflowResponse
from app.services.workflow_service import WorkflowService

router = APIRouter(prefix="/workflows", tags=["Workflows"])


@router.post("", response_model=WorkflowResponse)
async def create_workflow(
    data: WorkflowCreate,
    db: AsyncSession = Depends(get_postgres_db),
    current_user: User = Depends(get_current_user),
):
    workflow = await WorkflowService.create_workflow(db, current_user.id, data)
    return WorkflowResponse.model_validate(workflow)


@router.get("", response_model=list[WorkflowResponse])
async def list_workflows(
    db: AsyncSession = Depends(get_postgres_db),
    current_user: User = Depends(get_current_user),
):
    workflows = await WorkflowService.list_workflows(db, current_user.id)
    return [WorkflowResponse.model_validate(w) for w in workflows]


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(
    workflow_id: str,
    db: AsyncSession = Depends(get_postgres_db),
    current_user: User = Depends(get_current_user),
):
    workflow = await WorkflowService.get_workflow_for_user(
        db, workflow_id, current_user.id
    )
    if workflow is None:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return WorkflowResponse.model_validate(workflow)


@router.delete("/{workflow_id}", status_code=204)
async def delete_workflow(
    workflow_id: str,
    db: AsyncSession = Depends(get_postgres_db),
    current_user: User = Depends(get_current_user),
):
    deleted = await WorkflowService.delete_workflow_for_user(
        db, workflow_id, current_user.id
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="Workflow not found")
