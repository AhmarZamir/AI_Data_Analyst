from src.database.connection import execute_query
from src.llm.sql_generator import generate_sql



question = "how many total customers are there from karachi?"

sql = generate_sql(question)
print("Generated SQL Query:")
print(sql)

results = execute_query(sql)

for row in results:
    print(f"count: {row[0]}")

