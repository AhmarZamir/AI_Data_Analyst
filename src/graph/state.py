from typing import TypedDict, NotRequired, Any


class AgentState(TypedDict):

    question: str

    schema: NotRequired[str]

    sql: NotRequired[str]

    is_safe: NotRequired[bool]

    validation_message: NotRequired[str]

    result: NotRequired[list[Any]]

    answer: NotRequired[str]

    error: NotRequired[str]
    