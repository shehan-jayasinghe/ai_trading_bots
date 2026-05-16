from enum import StrEnum


class WorkflowStatus(StrEnum):
    DRAFT = "draft"
    EDIT = "edit"
    RUN = "run"
