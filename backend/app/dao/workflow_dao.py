import logging

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DatabaseError
from app.models.workflow_model import Workflow

logger = logging.getLogger(__name__)


class WorkflowDAO:
    @staticmethod
    async def create_workflow(db: AsyncSession, workflow_data: dict) -> Workflow:
        try:
            workflow = Workflow(**workflow_data)
            db.add(workflow)
            await db.commit()
            await db.refresh(workflow)
            return workflow
        except SQLAlchemyError as exc:
            await db.rollback()
            logger.exception("create_workflow failed")
            raise DatabaseError() from exc

    @staticmethod
    async def get_workflow(db: AsyncSession, workflow_id: str) -> Workflow | None:
        try:
            result = await db.execute(
                select(Workflow).where(Workflow.id == workflow_id)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as exc:
            logger.exception("get_workflow failed workflow_id=%s", workflow_id)
            raise DatabaseError() from exc

    @staticmethod
    async def list_workflows(db: AsyncSession, user_id: str) -> list[Workflow]:
        try:
            result = await db.execute(
                select(Workflow).where(Workflow.user_id == user_id)
            )
            return list(result.scalars().all())
        except SQLAlchemyError as exc:
            logger.exception("list_workflows failed user_id=%s", user_id)
            raise DatabaseError() from exc

    @staticmethod
    async def update_workflow(db: AsyncSession, workflow: Workflow) -> Workflow:
        try:
            await db.commit()
            await db.refresh(workflow)
            return workflow
        except SQLAlchemyError as exc:
            await db.rollback()
            logger.exception("update_workflow failed workflow_id=%s", workflow.id)
            raise DatabaseError() from exc

    @staticmethod
    async def delete_workflow(db: AsyncSession, workflow: Workflow) -> None:
        try:
            await db.delete(workflow)
            await db.commit()
        except SQLAlchemyError as exc:
            await db.rollback()
            logger.exception("delete_workflow failed workflow_id=%s", workflow.id)
            raise DatabaseError() from exc
