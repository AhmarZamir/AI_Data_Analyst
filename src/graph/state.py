from typing import Any, NotRequired, TypedDict


class AgentState(TypedDict):

    question: str

    schema: NotRequired[Any]

    sql: NotRequired[str]

    is_safe: NotRequired[bool]

    validation_message: NotRequired[str]

    result: NotRequired[list[Any]]

    answer: NotRequired[str]

    error: NotRequired[str]

    db_error: NotRequired[str]

    retry_count: NotRequired[int]

    is_complex: NotRequired[bool]

    plan: NotRequired[list[str]]

    current_step: NotRequired[int]

    step_results: NotRequired[list[Any]]

    active_question: NotRequired[str]
