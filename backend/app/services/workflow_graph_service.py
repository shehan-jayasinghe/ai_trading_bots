from app.core.exceptions import BadRequestError
from app.models.workflow_model import Workflow
from app.schemas.workflow_graph_schema import (
    AGENT_KINDS,
    WorkflowGraphDefinition,
)


class WorkflowGraphService:
    @staticmethod
    def validate_graph(graph: WorkflowGraphDefinition) -> None:
        if not graph.nodes:
            raise BadRequestError("Graph must contain at least one node")

        node_ids = {n.id for n in graph.nodes}
        for edge in graph.edges:
            if edge.source not in node_ids or edge.target not in node_ids:
                raise BadRequestError("Edge references unknown node")
            if edge.source == edge.target:
                raise BadRequestError("Edge cannot connect a node to itself")

        for node in graph.nodes:
            if node.type == "agent":
                kind = node.data.agent_kind
                if not kind or kind not in AGENT_KINDS:
                    raise BadRequestError(f"Invalid agent kind on node {node.id}")
            if node.parent_id and node.parent_id not in node_ids:
                raise BadRequestError(f"Node {node.id} has unknown parentId")
            if node.parent_id:
                parent = next(
                    (n for n in graph.nodes if n.id == node.parent_id), None
                )
                if parent is None or parent.type != "parallel":
                    raise BadRequestError(
                        f"Node {node.id} parent must be a parallel group"
                    )

        agent_count = sum(1 for n in graph.nodes if n.type == "agent")
        if agent_count < 1:
            raise BadRequestError("Graph must include at least one agent")

        kinds = {
            n.data.agent_kind
            for n in graph.nodes
            if n.type == "agent" and n.data.agent_kind
        }
        for required in ("data", "decision", "trading"):
            if required not in kinds:
                raise BadRequestError(
                    f"Graph must include at least one {required} agent"
                )

    @staticmethod
    def graph_from_workflow(workflow: Workflow) -> WorkflowGraphDefinition | None:
        if not workflow.graph_definition:
            return None
        return WorkflowGraphDefinition.model_validate(workflow.graph_definition)

    @staticmethod
    def ensure_runnable(workflow: Workflow) -> None:
        graph = WorkflowGraphService.graph_from_workflow(workflow)
        if graph is None:
            raise BadRequestError(
                "Save a valid agent graph in the editor first."
            )
        WorkflowGraphService.validate_graph(graph)

    @staticmethod
    def is_runnable(workflow: Workflow) -> bool:
        try:
            WorkflowGraphService.ensure_runnable(workflow)
        except BadRequestError:
            return False
        return True
