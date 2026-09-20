from src.database.connection import execute_query
from src.llm.sql_generator import generate_sql
from src.database.schema import get_tables , get_columns , format_schema



from src.retrieval.schema_retriever import retrieve_tables


question = "Which city generated the highest revenue?"


results = retrieve_tables(
    question
)

for result in results:

    print(
        result["table"],
        result["score"]
    )
    
#  question = "Which city generated the highest revenue?"

# sql = generate_sql(question)
# print("Generated SQL Query:")
# print(sql)

# results = execute_query(sql)

# for row in results:
#     print(row)

