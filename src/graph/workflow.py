from langgraph.graph import StateGraph, START, END

from src.graph.state import AgentState

from src.retrieval.schema_retriever import retrieve_tables
from src.llm.sql_generator import generate_sql
from src.sql.validator import validate_sql
from src.database.connection import execute_query
from src.llm.result_interpreter import interpret_result


def retrieve_schema_node(state: AgentState):

    question = state["question"]

    schema = retrieve_tables(question)

    return {
        "schema": schema
    }

def generate_sql_node(state: AgentState):

    question = state["question"]

    schema = state["schema"]

    sql = generate_sql(
        question=question,
        schema=schema
    )

    return {
        "sql": sql
    }



def validate_sql_node(state: AgentState):

    sql = state["sql"]

    is_safe, message = validate_sql(sql)

    return {
        "is_safe": is_safe,
        "validation_message": message
    }

def execute_sql_node(state: AgentState):

    sql = state["sql"]

    result = execute_query(sql)

    return {
        "result": result
    }


def interpret_result_node(state: AgentState):

    question = state["question"]

    sql = state["sql"]

    result = state["result"]

    answer = interpret_result(
        question=question,
        sql=sql,
        result=result
    )

    return {
        "answer": answer
    }


def reject_sql_node(state: AgentState):

    message = state["validation_message"]

    return {
        "answer": f"Query rejected: {message}",
        "error": message
    }


def route_after_validation(state: AgentState):

    if state["is_safe"]:
        return "execute_sql"

    return "reject_sql"




def build_graph():

    builder = StateGraph(AgentState)

    # Register nodes

    builder.add_node(
        "retrieve_schema",
        retrieve_schema_node
    )

    builder.add_node(
        "generate_sql",
        generate_sql_node
    )

    builder.add_node(
        "validate_sql",
        validate_sql_node
    )

    builder.add_node(
        "execute_sql",
        execute_sql_node
    )

    builder.add_node(
        "interpret_result",
        interpret_result_node
    )

    builder.add_node(
        "reject_sql",
        reject_sql_node
    )

    # Define execution order

    builder.add_edge(
        START,
        "retrieve_schema"
    )

    builder.add_edge(
        "retrieve_schema",
        "generate_sql"
    )

    builder.add_edge(
        "generate_sql",
        "validate_sql"
    )

    # Conditional routing

    builder.add_conditional_edges(
        "validate_sql",
        route_after_validation,
        {
            "execute_sql": "execute_sql",
            "reject_sql": "reject_sql"
        }
    )

    # Successful execution path

    builder.add_edge(
        "execute_sql",
        "interpret_result"
    )

    builder.add_edge(
        "interpret_result",
        END
    )

    # Rejection path

    builder.add_edge(
        "reject_sql",
        END
    )

    return builder.compile()


