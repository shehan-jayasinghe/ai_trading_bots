import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.dao.workflow_dao import WorkflowDAO
from app.models.workflow_model import Workflow
from app.models.workflow_status import WorkflowStatus
from app.schemas.workflow_schema import WorkflowCreate


class WorkflowService:
    """Persistence and ownership checks for workflows."""

    @staticmethod
    async def create_workflow(
        db: AsyncSession,
        user_id: str,
        data: WorkflowCreate,
    ) -> Workflow:
        workflow_data = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": data.name,
            "trading_pair": data.trading_pair,
            "trading_type": data.trading_type,
            "starting_time": data.starting_time,
            "one_day_minimum_trade": data.one_day_minimum_trade,
            "deriv_app_id": (data.deriv_app_id or "").strip() or None,
            "deriv_api_token": (data.deriv_api_token or "").strip() or None,
            "status": WorkflowStatus.DRAFT.value,
        }
        return await WorkflowDAO.create_workflow(db, workflow_data)

    @staticmethod
    async def get_workflow_for_user(
        db: AsyncSession,
        workflow_id: str,
        user_id: str,
    ) -> Workflow:
        workflow = await WorkflowDAO.get_workflow(db, workflow_id)
        if workflow is None or workflow.user_id != user_id:
            raise NotFoundError("Workflow not found")
        return workflow

    @staticmethod
    async def list_workflows(db: AsyncSession, user_id: str) -> list[Workflow]:
        return await WorkflowDAO.list_workflows(db, user_id)
