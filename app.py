import streamlit as st

from src.graph.workflow import analyst_graph


st.set_page_config(
    page_title="AI Data Analyst",
    page_icon="📊",
    layout="wide"
)


st.title("📊 AI Data Analyst")

st.caption(
    "Ask questions about your business data in plain English."
)


if "messages" not in st.session_state:

    st.session_state.messages = []


for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.write(message["content"])

        if message.get("resolved_question"):

            with st.expander(
                "View interpreted question"
            ):

                st.write(
                    message["resolved_question"]
                )

        if message.get("plan"):

            with st.expander("View analysis plan"):

                for index, step in enumerate(
                    message["plan"],
                    start=1
                ):

                    st.write(
                        f"{index}. {step}"
                    )

        if message.get("sql"):

            with st.expander("View generated SQL"):

                st.code(
                    message["sql"],
                    language="sql"
                )

        if "result" in message:

            with st.expander("View database result"):

                st.write(message["result"])


question = st.chat_input(
    "Ask something about your business..."
)


if question:

    conversation_history = [
        {
            "role": message["role"],
            "content": message["content"]
        }
        for message in st.session_state.messages
    ]

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    with st.chat_message("user"):

        st.write(question)


    with st.chat_message("assistant"):

        try:

            with st.spinner(
                "Analyzing your question..."
            ):

                graph_result = analyst_graph.invoke(
                    {
                        "question": question,
                        "conversation_history": conversation_history,
                        "retry_count": 0,
                        "db_error": "",
                        "error": ""
                    },
                    config={
                        "recursion_limit": 50
                    }
                )

            answer = graph_result["answer"]
            sql = graph_result.get("sql")
            result = graph_result.get("result")
            error = graph_result.get("error")
            plan = graph_result.get("plan", [])
            is_complex = graph_result.get(
                "is_complex",
                False
            )
            resolved_question = graph_result.get(
                "resolved_question"
            )

            if error:

                st.warning(answer)

            else:

                st.write(answer)

            if (
                resolved_question
                and resolved_question != question
            ):

                with st.expander(
                    "View interpreted question"
                ):

                    st.write(
                        resolved_question
                    )

            if plan:

                with st.expander(
                    "View analysis plan"
                ):

                    for index, step in enumerate(
                        plan,
                        start=1
                    ):

                        st.write(
                            f"{index}. {step}"
                        )

            if sql and not is_complex:

                with st.expander(
                    "View generated SQL"
                ):

                    st.code(
                        sql,
                        language="sql"
                    )

            if (
                result is not None
                and not error
                and not is_complex
            ):

                with st.expander(
                    "View database result"
                ):

                    st.write(result)

            message = {
                "role": "assistant",
                "content": answer
            }

            if (
                resolved_question
                and resolved_question != question
            ):

                message["resolved_question"] = (
                    resolved_question
                )

            if plan:

                message["plan"] = plan

            if sql and not is_complex:

                message["sql"] = sql

            if (
                result is not None
                and not error
                and not is_complex
            ):

                message["result"] = result

            st.session_state.messages.append(
                message
            )


        except Exception as error:

            error_message = (
                f"Something went wrong: {error}"
            )

            st.error(error_message)

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": error_message
                }
            )
