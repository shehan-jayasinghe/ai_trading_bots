from enum import StrEnum


class WorkflowStatus(StrEnum):
    DRAFT = "draft"
    EDIT = "edit"
    COMPLETED = "completed"
    RUN = "run"
