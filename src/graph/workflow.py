import psycopg2
from langgraph.graph import END, START, StateGraph

from src.database.connection import execute_query
from src.graph.state import AgentState
from src.llm.analysis_synthesizer import synthesize_analysis
from src.llm.context_resolver import resolve_question
from src.llm.query_planner import create_plan
from src.llm.result_interpreter import interpret_result
from src.llm.sql_generator import generate_sql
from src.llm.sql_repair import repair_sql
from src.retrieval.schema_retriever import retrieve_tables
from src.sql.validator import validate_sql


MAX_RETRIES = 2


def resolve_question_node(state: AgentState):

    resolved_question = resolve_question(
        question=state["question"],
        conversation_history=state.get(
            "conversation_history",
            []
        )
    )

    return {
        "resolved_question": resolved_question
    }


def retrieve_schema_node(state: AgentState):

    question = state.get(
        "resolved_question",
        state["question"]
    )

    schema = retrieve_tables(
        question
    )

    return {
        "schema": schema
    }


def plan_query_node(state: AgentState):

    question = state.get(
        "resolved_question",
        state["question"]
    )

    plan = create_plan(
        question=question,
        schema=state["schema"]
    )

    return {
        "is_complex": plan["is_complex"],
        "plan": plan["steps"],
        "current_step": 0,
        "step_results": []
    }


def prepare_step_node(state: AgentState):

    current_step = state["current_step"]
    active_question = state["plan"][current_step]

    return {
        "active_question": active_question,
        "retry_count": 0,
        "db_error": "",
        "error": ""
    }


def generate_sql_node(state: AgentState):

    base_question = state.get(
        "resolved_question",
        state["question"]
    )

    question = state.get(
        "active_question",
        base_question
    )

    sql = generate_sql(
        question=question,
        schema=state["schema"]
    )

    return {
        "sql": sql
    }


def validate_sql_node(state: AgentState):

    is_safe, message = validate_sql(
        state["sql"]
    )

    return {
        "is_safe": is_safe,
        "validation_message": message
    }


def execute_sql_node(state: AgentState):

    try:

        result = execute_query(
            state["sql"]
        )

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

    retry_count = state.get(
        "retry_count",
        0
    )

    base_question = state.get(
        "resolved_question",
        state["question"]
    )

    question = state.get(
        "active_question",
        base_question
    )

    corrected_sql = repair_sql(
        question=question,
        schema=state["schema"],
        failed_sql=state["sql"],
        db_error=state["db_error"]
    )

    return {
        "sql": corrected_sql,
        "retry_count": retry_count + 1,
        "db_error": ""
    }


def store_step_result_node(state: AgentState):

    step_results = list(
        state.get("step_results", [])
    )

    current_step = state["current_step"]

    step_results.append(
        {
            "question": state["plan"][current_step],
            "sql": state["sql"],
            "result": state["result"]
        }
    )

    return {
        "step_results": step_results,
        "current_step": current_step + 1
    }


def combine_results_node(state: AgentState):

    question = state.get(
        "resolved_question",
        state["question"]
    )

    answer = synthesize_analysis(
        question=question,
        step_results=state["step_results"]
    )

    return {
        "answer": answer,
        "error": ""
    }


def interpret_result_node(state: AgentState):

    question = state.get(
        "resolved_question",
        state["question"]
    )

    answer = interpret_result(
        question=question,
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

    retry_count = state.get(
        "retry_count",
        0
    )

    return {
        "answer": (
            "I couldn't execute the analytical query after attempting "
            "to correct it. Please try rephrasing your question."
        ),
        "error": (
            f"SQL execution failed after {retry_count} repair attempts."
        )
    }


def route_after_planning(state: AgentState):

    if state["is_complex"]:
        return "prepare_step"

    return "generate_sql"


def route_after_validation(state: AgentState):

    if state["is_safe"]:
        return "execute_sql"

    return "reject_sql"


def route_after_execution(state: AgentState):

    db_error = state.get(
        "db_error",
        ""
    )

    retry_count = state.get(
        "retry_count",
        0
    )

    if db_error:

        if retry_count < MAX_RETRIES:
            return "repair_sql"

        return "failed_sql"

    if state.get("is_complex", False):
        return "store_step_result"

    return "interpret_result"


def route_after_step(state: AgentState):

    if state["current_step"] < len(
        state["plan"]
    ):
        return "prepare_step"

    return "combine_results"


def build_graph():

    builder = StateGraph(AgentState)

    builder.add_node(
        "resolve_question",
        resolve_question_node
    )

    builder.add_node(
        "retrieve_schema",
        retrieve_schema_node
    )

    builder.add_node(
        "plan_query",
        plan_query_node
    )

    builder.add_node(
        "prepare_step",
        prepare_step_node
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
        "repair_sql",
        repair_sql_node
    )

    builder.add_node(
        "store_step_result",
        store_step_result_node
    )

    builder.add_node(
        "combine_results",
        combine_results_node
    )

    builder.add_node(
        "interpret_result",
        interpret_result_node
    )

    builder.add_node(
        "reject_sql",
        reject_sql_node
    )

    builder.add_node(
        "failed_sql",
        failed_sql_node
    )

    builder.add_edge(
        START,
        "resolve_question"
    )

    builder.add_edge(
        "resolve_question",
        "retrieve_schema"
    )

    builder.add_edge(
        "retrieve_schema",
        "plan_query"
    )

    builder.add_conditional_edges(
        "plan_query",
        route_after_planning,
        {
            "generate_sql": "generate_sql",
            "prepare_step": "prepare_step"
        }
    )

    builder.add_edge(
        "prepare_step",
        "generate_sql"
    )

    builder.add_edge(
        "generate_sql",
        "validate_sql"
    )

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
            "store_step_result": "store_step_result",
            "repair_sql": "repair_sql",
            "failed_sql": "failed_sql"
        }
    )

    builder.add_edge(
        "repair_sql",
        "validate_sql"
    )

    builder.add_conditional_edges(
        "store_step_result",
        route_after_step,
        {
            "prepare_step": "prepare_step",
            "combine_results": "combine_results"
        }
    )

    builder.add_edge(
        "interpret_result",
        END
    )

    builder.add_edge(
        "combine_results",
        END
    )

    builder.add_edge(
        "reject_sql",
        END
    )

    builder.add_edge(
        "failed_sql",
        END
    )

    return builder.compile()


analyst_graph = build_graph()
