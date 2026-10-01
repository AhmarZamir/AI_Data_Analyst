import psycopg2
from langgraph.graph import END, START, StateGraph

from src.database.connection import execute_query
from src.graph.state import AgentState
from src.llm.result_interpreter import interpret_result
from src.llm.sql_generator import generate_sql
from src.llm.sql_repair import repair_sql
from src.retrieval.schema_retriever import retrieve_tables
from src.sql.validator import validate_sql


MAX_RETRIES = 2


def retrieve_schema_node(state: AgentState):

    question = state["question"]

    schema = retrieve_tables(question)

    return {
        "schema": schema
    }


def generate_sql_node(state: AgentState):

    sql = generate_sql(
        question=state["question"],
        schema=state["schema"]
    )

    return {
        "sql": sql
    }


def validate_sql_node(state: AgentState):

    is_safe, message = validate_sql(state["sql"])

    return {
        "is_safe": is_safe,
        "validation_message": message
    }


def execute_sql_node(state: AgentState):

    try:

        result = execute_query(state["sql"])

        return {
            "result": result,
            "db_error": ""
        }

    except psycopg2.Error as error:

        return {
            "result": [],
            "db_error": str(error)
        }


def repair_sql_node(state: AgentState):

    retry_count = state.get("retry_count", 0)

    corrected_sql = repair_sql(
        question=state["question"],
        schema=state["schema"],
        failed_sql=state["sql"],
        db_error=state["db_error"]
    )

    return {
        "sql": corrected_sql,
        "retry_count": retry_count + 1,
        "db_error": ""
    }


def interpret_result_node(state: AgentState):

    answer = interpret_result(
        question=state["question"],
        sql=state["sql"],
        result=state["result"]
    )

    return {
        "answer": answer,
        "error": ""
    }


def reject_sql_node(state: AgentState):

    message = state["validation_message"]

    return {
        "answer": f"Query rejected: {message}",
        "error": message
    }


def failed_sql_node(state: AgentState):

    retry_count = state.get("retry_count", 0)

    return {
        "answer": (
            "I couldn't execute the analytical query after attempting "
            "to correct it. Please try rephrasing your question."
        ),
        "error": (
            f"SQL execution failed after {retry_count} repair attempts."
        )
    }


def route_after_validation(state: AgentState):

    if state["is_safe"]:
        return "execute_sql"

    return "reject_sql"


def route_after_execution(state: AgentState):

    db_error = state.get("db_error", "")
    retry_count = state.get("retry_count", 0)

    if not db_error:
        return "interpret_result"

    if retry_count < MAX_RETRIES:
        return "repair_sql"

    return "failed_sql"


def build_graph():

    builder = StateGraph(AgentState)

    builder.add_node("retrieve_schema", retrieve_schema_node)
    builder.add_node("generate_sql", generate_sql_node)
    builder.add_node("validate_sql", validate_sql_node)
    builder.add_node("execute_sql", execute_sql_node)
    builder.add_node("repair_sql", repair_sql_node)
    builder.add_node("interpret_result", interpret_result_node)
    builder.add_node("reject_sql", reject_sql_node)
    builder.add_node("failed_sql", failed_sql_node)

    builder.add_edge(START, "retrieve_schema")
    builder.add_edge("retrieve_schema", "generate_sql")
    builder.add_edge("generate_sql", "validate_sql")

    builder.add_conditional_edges(
        "validate_sql",
        route_after_validation,
        {
            "execute_sql": "execute_sql",
            "reject_sql": "reject_sql"
        }
    )

    builder.add_conditional_edges(
        "execute_sql",
        route_after_execution,
        {
            "interpret_result": "interpret_result",
            "repair_sql": "repair_sql",
            "failed_sql": "failed_sql"
        }
    )

    builder.add_edge("repair_sql", "validate_sql")
    builder.add_edge("interpret_result", END)
    builder.add_edge("reject_sql", END)
    builder.add_edge("failed_sql", END)

    return builder.compile()


analyst_graph = build_graph()
