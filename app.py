import streamlit as st

from src.database.connection import execute_query
from src.llm.sql_generator import generate_sql
from src.sql.validator import validate_sql
from src.llm.result_interpreter import interpret_result

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

        if "result" in message:

            with st.expander(
                "View database result"
            ):

                st.write(
                    message["result"])        


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

                isSafe , validation_message = validate_sql(sql)

                if not isSafe:
                    st.warning(validation_message)
                    result = None
                    answer = None
                else:
                    result = execute_query(sql)
                    answer =  interpret_result(result=result, sql=sql, question=question)
                    
                    


                if answer is not None:
                   st.write(answer)


            with st.expander(
                "View generated SQL"
            ):

                st.code(
                    sql,
                    language="sql"
                )


            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": answer,
                    "sql": sql,
                    "result": str(result)
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