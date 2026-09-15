from src.database.connection import execute_query


query ="""
SELECT
    city,
    COUNT(*)
FROM customers
GROUP BY city
ORDER BY COUNT(*) DESC;
"""


results = execute_query(query)

for row in results:
    print(f"City: {row[0]}, Count: {row[1]}")

