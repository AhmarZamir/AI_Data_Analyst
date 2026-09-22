from sentence_transformers import SentenceTransformer
from sentence_transformers import SentenceTransformer, util

from src.database.schema import get_table_documents , get_foreign_keys



model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)


def build_schema_index():

    documents = get_table_documents()

    table_names = list(
        documents.keys()
    )

    document_texts = list(
        documents.values()
    )


    embeddings = model.encode(
        document_texts
    )


    return (
        table_names,
        document_texts,
        embeddings
    )


def retrieve_tables(
    question,
    top_k=3
):

    (
        table_names,
        document_texts,
        table_embeddings
    ) = build_schema_index()


    question_embedding = model.encode(
        question
    )


    scores = util.cos_sim(
        question_embedding,
        table_embeddings
    )[0]


    ranked_indices = scores.argsort(
        descending=True
    )


    selected_tables = []


    for index in ranked_indices[:top_k]:

        index = int(index)

        selected_tables.append(
            {
                "table": table_names[index],
                "schema": document_texts[index],
                "score": float(scores[index])
            }
        )


    return selected_tables


def expand_related_tables(
    table_names
):

    foreign_keys = get_foreign_keys()

    expanded = set(
        table_names
    )


    for (
        source_table,
        source_column,
        target_table,
        target_column
    ) in foreign_keys:

        if source_table in table_names:

            expanded.add(
                target_table
            )


        if target_table in table_names:

            expanded.add(
                source_table
            )


    return expanded