from typing import Any, Literal, Optional

from pydantic import BaseModel, Field

AGENT_KINDS = frozenset(
    {"data", "indicator", "rag", "decision", "mm", "trading", "rag_write"}
)


class GraphNodePosition(BaseModel):
    x: float
    y: float


class GraphNodeData(BaseModel):
    label: str
    agent_kind: Optional[str] = Field(None, alias="agentKind")

    model_config = {"populate_by_name": True}


class GraphNodeStyle(BaseModel):
    width: Optional[float] = None
    height: Optional[float] = None


class GraphNode(BaseModel):
    id: str
    type: Literal["agent", "parallel"]
    position: GraphNodePosition
    data: GraphNodeData
    parent_id: Optional[str] = Field(None, alias="parentId")
    style: Optional[GraphNodeStyle] = None

    model_config = {"populate_by_name": True}


class GraphEdge(BaseModel):
    id: str
    source: str
    target: str


class WorkflowGraphDefinition(BaseModel):
    version: Literal[1] = 1
    nodes: list[GraphNode] = Field(default_factory=list)
    edges: list[GraphEdge] = Field(default_factory=list)

    def model_dump_for_db(self) -> dict[str, Any]:
        return self.model_dump(by_alias=True, mode="json")
