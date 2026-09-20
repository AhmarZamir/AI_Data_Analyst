from src.database.connection import execute_query
from src.llm.sql_generator import generate_sql
from src.database.schema import get_tables , get_columns , format_schema




print("Available tables in the database:")

for table in get_tables():
    print(f" - {table}")

print("\nAvailable columns in the database:")
print(get_columns())


print("\nFormatted database schema:")
print(format_schema())
 
#  question = "Which city generated the highest revenue?"

# sql = generate_sql(question)
# print("Generated SQL Query:")
# print(sql)

# results = execute_query(sql)

# for row in results:
#     print(row)

