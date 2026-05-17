from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestError, ConfigurationError
from app.dao.workflow_dao import WorkflowDAO
from app.messaging.kafka_publisher import publish_workflow_scheduled
from app.models.workflow_model import Workflow
from app.models.workflow_status import WorkflowStatus
from app.schemas.workflow_graph_schema import WorkflowGraphDefinition
from app.schemas.workflow_schema import WorkflowCreate, WorkflowUpdate
from app.services.workflow_graph_service import WorkflowGraphService
from app.services.workflow_service import WorkflowService


class WorkflowHandler:
    @staticmethod
    async def create(
        db: AsyncSession,
        user_id: str,
        data: WorkflowCreate,
    ) -> Workflow:
        return await WorkflowService.create_workflow(db, user_id, data)

    @staticmethod
    async def list_for_user(db: AsyncSession, user_id: str) -> list[Workflow]:
        return await WorkflowService.list_workflows(db, user_id)

    @staticmethod
    async def get(
        db: AsyncSession,
        workflow_id: str,
        user_id: str,
    ) -> Workflow:
        return await WorkflowService.get_workflow_for_user(db, workflow_id, user_id)

    @staticmethod
    async def begin_edit(
        db: AsyncSession,
        workflow_id: str,
        user_id: str,
    ) -> Workflow:
        workflow = await WorkflowService.get_workflow_for_user(
            db, workflow_id, user_id
        )
        if workflow.status == WorkflowStatus.RUN.value:
            raise BadRequestError("Cannot edit a workflow that is running")
        workflow.status = WorkflowStatus.EDIT.value
        return await WorkflowDAO.update_workflow(db, workflow)

    @staticmethod
    async def update_metadata(
        db: AsyncSession,
        workflow_id: str,
        user_id: str,
        data: WorkflowUpdate,
    ) -> Workflow:
        workflow = await WorkflowService.get_workflow_for_user(
            db, workflow_id, user_id
        )
        if workflow.status == WorkflowStatus.RUN.value:
            raise BadRequestError("Cannot update a workflow that is running")

        updates = data.model_dump(exclude_unset=True)
        if not updates:
            raise BadRequestError("No fields to update")

        for field, value in updates.items():
            if field == "deriv_api_token" and (value is None or str(value).strip() == ""):
                continue
            if field in ("deriv_app_id", "deriv_api_token") and value is not None:
                value = str(value).strip() or None
            setattr(workflow, field, value)
        workflow.status = WorkflowStatus.EDIT.value
        return await WorkflowDAO.update_workflow(db, workflow)

    @staticmethod
    async def complete(
        db: AsyncSession,
        workflow_id: str,
        user_id: str,
    ) -> Workflow:
        workflow = await WorkflowService.get_workflow_for_user(
            db, workflow_id, user_id
        )
        if workflow.status == WorkflowStatus.RUN.value:
            raise BadRequestError("Cannot complete a workflow that is running")
        if workflow.status == WorkflowStatus.COMPLETED.value:
            raise BadRequestError("Workflow is already completed")
        if workflow.status not in (
            WorkflowStatus.DRAFT.value,
            WorkflowStatus.EDIT.value,
        ):
            raise BadRequestError("Workflow cannot be completed from this state")

        WorkflowGraphService.ensure_runnable(workflow)

        app_id = (workflow.deriv_app_id or "").strip()
        token = (workflow.deriv_api_token or "").strip()
        if not app_id or not token:
            raise BadRequestError(
                "Deriv app ID and API token are required before completing the workflow"
            )

        workflow.status = WorkflowStatus.COMPLETED.value
        return await WorkflowDAO.update_workflow(db, workflow)

    @staticmethod
    async def run(
        db: AsyncSession,
        workflow_id: str,
        user_id: str,
    ) -> Workflow:
        workflow = await WorkflowService.get_workflow_for_user(
            db, workflow_id, user_id
        )
        if workflow.status == WorkflowStatus.RUN.value:
            raise BadRequestError("Workflow is already running")
        if workflow.status != WorkflowStatus.COMPLETED.value:
            raise BadRequestError(
                "Workflow must be completed before it can be started"
            )
        if not (workflow.deriv_app_id or "").strip() or not (
            workflow.deriv_api_token or ""
        ).strip():
            raise BadRequestError(
                "Deriv app ID and API token are required before running the workflow"
            )

        workflow.status = WorkflowStatus.RUN.value
        workflow = await WorkflowDAO.update_workflow(db, workflow)

        try:
            await publish_workflow_scheduled(workflow, user_id)
        except Exception as exc:
            workflow.status = WorkflowStatus.COMPLETED.value
            await WorkflowDAO.update_workflow(db, workflow)
            raise ConfigurationError(
                "Workflow could not be scheduled; Kafka publish failed"
            ) from exc

        return workflow

    @staticmethod
    async def delete(
        db: AsyncSession,
        workflow_id: str,
        user_id: str,
    ) -> None:
        workflow = await WorkflowService.get_workflow_for_user(
            db, workflow_id, user_id
        )
        await WorkflowDAO.delete_workflow(db, workflow)

    @staticmethod
    async def get_graph(
        db: AsyncSession,
        workflow_id: str,
        user_id: str,
    ) -> WorkflowGraphDefinition | None:
        workflow = await WorkflowService.get_workflow_for_user(
            db, workflow_id, user_id
        )
        return WorkflowGraphService.graph_from_workflow(workflow)

    @staticmethod
    async def save_graph(
        db: AsyncSession,
        workflow_id: str,
        user_id: str,
        graph: WorkflowGraphDefinition,
    ) -> WorkflowGraphDefinition:
        workflow = await WorkflowService.get_workflow_for_user(
            db, workflow_id, user_id
        )
        if workflow.status == WorkflowStatus.RUN.value:
            raise BadRequestError("Cannot edit graph while workflow is running")

        WorkflowGraphService.validate_graph(graph)
        workflow.graph_definition = graph.model_dump_for_db()
        if workflow.status == WorkflowStatus.DRAFT.value:
            workflow.status = WorkflowStatus.EDIT.value
        await WorkflowDAO.update_workflow(db, workflow)
        return graph
