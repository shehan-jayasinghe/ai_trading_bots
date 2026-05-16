from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependencies import get_postgres_db
from app.middleware.auth import get_current_user
from app.models.user_model import User
from app.schemas.workflow_schema import (
    WorkflowCreate,
    WorkflowResponse,
    WorkflowUpdate,
)
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
    return WorkflowResponse.model_validate(workflow)


@router.patch("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(
    workflow_id: str,
    data: WorkflowUpdate,
    db: AsyncSession = Depends(get_postgres_db),
    current_user: User = Depends(get_current_user),
):
    workflow = await WorkflowService.update_workflow(
        db, workflow_id, current_user.id, data
    )
    return WorkflowResponse.model_validate(workflow)


@router.post("/{workflow_id}/edit", response_model=WorkflowResponse)
async def begin_edit_workflow(
    workflow_id: str,
    db: AsyncSession = Depends(get_postgres_db),
    current_user: User = Depends(get_current_user),
):
    workflow = await WorkflowService.begin_edit_workflow(
        db, workflow_id, current_user.id
    )
    return WorkflowResponse.model_validate(workflow)


@router.post("/{workflow_id}/run", response_model=WorkflowResponse)
async def run_workflow(
    workflow_id: str,
    db: AsyncSession = Depends(get_postgres_db),
    current_user: User = Depends(get_current_user),
):
    workflow = await WorkflowService.run_workflow(
        db, workflow_id, current_user.id
    )
    return WorkflowResponse.model_validate(workflow)


@router.delete("/{workflow_id}", status_code=204)
async def delete_workflow(
    workflow_id: str,
    db: AsyncSession = Depends(get_postgres_db),
    current_user: User = Depends(get_current_user),
):
    await WorkflowService.delete_workflow_for_user(
        db, workflow_id, current_user.id
    )
