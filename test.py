from src.graph.workflow import build_graph 


question = "How many customers joined last month?"


result = build_graph.invoke(
    {
        "question": question
    }
)


print("\nGenerated SQL:")
print(result.get("sql"))


print("\nValidation:")
print(result.get("validation_message"))


print("\nDatabase Result:")
print(result.get("result"))


print("\nFinal Answer:")
print(result.get("answer"))