from src.database.connection import execute_query
from src.llm.sql_generator import generate_sql



question = "Which city generated the highest revenue?"

sql = generate_sql(question)
print("Generated SQL Query:")
print(sql)

results = execute_query(sql)

for row in results:
    print(row)

