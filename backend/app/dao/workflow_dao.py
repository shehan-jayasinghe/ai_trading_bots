from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.workflow_model import Workflow


class WorkflowDAO:
    @staticmethod
    async def create_workflow(db: AsyncSession, workflow_data: dict) -> Workflow:
        workflow = Workflow(**workflow_data)
        db.add(workflow)
        await db.commit()
        await db.refresh(workflow)
        return workflow

    @staticmethod
    async def get_workflow(db: AsyncSession, workflow_id: str) -> Workflow | None:
        result = await db.execute(
            select(Workflow).where(Workflow.id == workflow_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_workflows(db: AsyncSession, user_id: str) -> list[Workflow]:
        result = await db.execute(
            select(Workflow).where(Workflow.user_id == user_id)
        )
        return list(result.scalars().all())

    @staticmethod
    async def delete_workflow(db: AsyncSession, workflow: Workflow) -> None:
        await db.delete(workflow)
        await db.commit()
