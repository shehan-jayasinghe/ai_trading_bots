from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependencies import get_postgres_db
from app.handlers.workflow_handler import WorkflowHandler
from app.middleware.auth import get_current_user
from app.models.user_model import User
from app.schemas.workflow_graph_schema import WorkflowGraphDefinition
from app.schemas.workflow_schema import (
    WorkflowCreate,
    WorkflowResponse,
    WorkflowUpdate,
)

router = APIRouter(prefix="/workflows", tags=["Workflows"])


@router.post("", response_model=WorkflowResponse)
async def create_workflow(
    data: WorkflowCreate,
    db: AsyncSession = Depends(get_postgres_db),
    current_user: User = Depends(get_current_user),
):
    workflow = await WorkflowHandler.create(db, current_user.id, data)
    return WorkflowResponse.model_validate(workflow)


@router.get("", response_model=list[WorkflowResponse])
async def list_workflows(
    db: AsyncSession = Depends(get_postgres_db),
    current_user: User = Depends(get_current_user),
):
    workflows = await WorkflowHandler.list_for_user(db, current_user.id)
    return [WorkflowResponse.model_validate(w) for w in workflows]


@router.get("/{workflow_id}/graph", response_model=WorkflowGraphDefinition | None)
async def get_workflow_graph(
    workflow_id: str,
    db: AsyncSession = Depends(get_postgres_db),
    current_user: User = Depends(get_current_user),
):
    return await WorkflowHandler.get_graph(db, workflow_id, current_user.id)


@router.put("/{workflow_id}/graph", response_model=WorkflowGraphDefinition)
async def update_workflow_graph(
    workflow_id: str,
    graph: WorkflowGraphDefinition,
    db: AsyncSession = Depends(get_postgres_db),
    current_user: User = Depends(get_current_user),
):
    return await WorkflowHandler.save_graph(db, workflow_id, current_user.id, graph)


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(
    workflow_id: str,
    db: AsyncSession = Depends(get_postgres_db),
    current_user: User = Depends(get_current_user),
):
    workflow = await WorkflowHandler.get(db, workflow_id, current_user.id)
    return WorkflowResponse.model_validate(workflow)


@router.patch("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(
    workflow_id: str,
    data: WorkflowUpdate,
    db: AsyncSession = Depends(get_postgres_db),
    current_user: User = Depends(get_current_user),
):
    workflow = await WorkflowHandler.update_metadata(
        db, workflow_id, current_user.id, data
    )
    return WorkflowResponse.model_validate(workflow)


@router.post("/{workflow_id}/edit", response_model=WorkflowResponse)
async def begin_edit_workflow(
    workflow_id: str,
    db: AsyncSession = Depends(get_postgres_db),
    current_user: User = Depends(get_current_user),
):
    workflow = await WorkflowHandler.begin_edit(db, workflow_id, current_user.id)
    return WorkflowResponse.model_validate(workflow)


@router.post("/{workflow_id}/complete", response_model=WorkflowResponse)
async def complete_workflow(
    workflow_id: str,
    db: AsyncSession = Depends(get_postgres_db),
    current_user: User = Depends(get_current_user),
):
    workflow = await WorkflowHandler.complete(db, workflow_id, current_user.id)
    return WorkflowResponse.model_validate(workflow)


@router.post("/{workflow_id}/run", response_model=WorkflowResponse)
async def run_workflow(
    workflow_id: str,
    db: AsyncSession = Depends(get_postgres_db),
    current_user: User = Depends(get_current_user),
):
    workflow = await WorkflowHandler.run(db, workflow_id, current_user.id)
    return WorkflowResponse.model_validate(workflow)


@router.delete("/{workflow_id}", status_code=204)
async def delete_workflow(
    workflow_id: str,
    db: AsyncSession = Depends(get_postgres_db),
    current_user: User = Depends(get_current_user),
):
    await WorkflowHandler.delete(db, workflow_id, current_user.id)
