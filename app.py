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


# Initialize conversation history

if "messages" not in st.session_state:

    st.session_state.messages = []


# Display previous messages

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.write(message["content"])

        if message.get("sql"):

            with st.expander("View generated SQL"):

                st.code(
                    message["sql"],
                    language="sql"
                )

        if "result" in message:

            with st.expander("View database result"):

                st.write(message["result"])


# Receive user question

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

            with st.spinner("Analyzing your question..."):

                # Execute the complete LangGraph workflow

                graph_result = analyst_graph.invoke(
                    {
                        "question": question
                    }
                )

            answer = graph_result["answer"]

            sql = graph_result.get("sql")

            result = graph_result.get("result")

            error = graph_result.get("error")


            if error:

                st.warning(answer)

            else:

                st.write(answer)


            if sql:

                with st.expander("View generated SQL"):

                    st.code(
                        sql,
                        language="sql"
                    )


            if result is not None:

                with st.expander("View database result"):

                    st.write(result)


            # Save response in session history

            message = {
                "role": "assistant",
                "content": answer
            }

            if sql:

                message["sql"] = sql

            if result is not None:

                message["result"] = result

            st.session_state.messages.append(message)


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