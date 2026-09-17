import streamlit as st

from src.database.connection import execute_query
from src.llm.sql_generator import generate_sql
from src.sql.validator import validate_sql


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

    with st.chat_message(
        message["role"]
    ):

        st.write(
            message["content"]
        )

        if "sql" in message:

            with st.expander(
                "View generated SQL"
            ):

                st.code(
                    message["sql"],
                    language="sql"
                )


question = st.chat_input(
    "Ask something about your business..."
)


if question:

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

                sql = generate_sql(
                    question
                )

                is_safe, validation_message = validate_sql(
                    sql
                )

                if is_safe:

                    result = execute_query(
                        sql
                    )

                else:

                    result = None


            with st.expander(
                "View generated SQL"
            ):

                st.code(
                    sql,
                    language="sql"
                )


            if result is not None:

                st.write(result)

                assistant_message = str(result)

            else:

                st.warning(validation_message)

                assistant_message = validation_message


            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": assistant_message,
                    "sql": sql
                }
            )


        except Exception as error:

            error_message = (
                f"Something went wrong: {error}"
            )

            st.error(
                error_message
            )


            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": error_message
                }
            )
