from src.database.connection import get_connection


def get_tables():

    query = """
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = 'public'
    AND table_type = 'BASE TABLE'
    ORDER BY table_name;
    """

    with get_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute(query)

            rows = cursor.fetchall()

    return [
        row[0]
        for row in rows
    ]

def get_columns():

    query = """
    SELECT
        table_name,
        column_name,
        data_type
    FROM information_schema.columns
    WHERE table_schema = 'public'
    ORDER BY table_name, ordinal_position;
    """

    with get_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute(query)

            rows = cursor.fetchall()


    schema = {}


    for table_name, column_name, data_type in rows:

        if table_name not in schema:

            schema[table_name] = []


        schema[table_name].append(
            {
                "name": column_name,
                "type": data_type
            }
        )


    return schema


def get_foreign_keys():

    query = """
    SELECT
        tc.table_name,
        kcu.column_name,
        ccu.table_name AS foreign_table_name,
        ccu.column_name AS foreign_column_name

    FROM information_schema.table_constraints AS tc

    JOIN information_schema.key_column_usage AS kcu
        ON tc.constraint_name = kcu.constraint_name
        AND tc.table_schema = kcu.table_schema

    JOIN information_schema.constraint_column_usage AS ccu
        ON ccu.constraint_name = tc.constraint_name
        AND ccu.table_schema = tc.table_schema

    WHERE tc.constraint_type = 'FOREIGN KEY'
    AND tc.table_schema = 'public';
    """


    with get_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute(query)

            rows = cursor.fetchall()


    return rows


def get_primary_keys():

    query = """
    SELECT
        tc.table_name,
        kcu.column_name

    FROM information_schema.table_constraints AS tc

    JOIN information_schema.key_column_usage AS kcu
        ON tc.constraint_name = kcu.constraint_name
        AND tc.table_schema = kcu.table_schema

    WHERE tc.constraint_type = 'PRIMARY KEY'
    AND tc.table_schema = 'public';
    """


    with get_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute(query)

            rows = cursor.fetchall()


    return rows



def inspect_schema():

    columns = get_columns()

    primary_keys = get_primary_keys()

    foreign_keys = get_foreign_keys()


    return {
        "columns": columns,
        "primary_keys": primary_keys,
        "foreign_keys": foreign_keys
    }


def format_schema():
    
    columns = get_columns()

    primary_keys = get_primary_keys()

    foreign_keys = get_foreign_keys()


    primary_key_map = {
        table: column
        for table, column in primary_keys
    }


    lines = []


    for table_name, table_columns in columns.items():

        lines.append(
            f"Table: {table_name}"
        )


        for column in table_columns:

            column_name = column["name"]

            data_type = column["type"]


            line = (
                f"- {column_name} ({data_type})"
            )


            if primary_key_map.get(table_name) == column_name:

                line += " PRIMARY KEY"


            lines.append(line)


        lines.append("")


    lines.append(
        "Relationships:"
    )


    for (
        table,
        column,
        foreign_table,
        foreign_column
    ) in foreign_keys:

        lines.append(
            f"- {table}.{column} -> "
            f"{foreign_table}.{foreign_column}"
        )


    return "\n".join(lines)


def get_table_names():

    return set(
        get_tables()
    )


def get_table_documents():

    columns = get_columns()
    foreign_keys = get_foreign_keys()

    documents = {}


    for table_name, table_columns in columns.items():

        lines = [
            f"Table: {table_name}",
            "Columns:"
        ]


        for column in table_columns:

            lines.append(
                f"- {column['name']} ({column['type']})"
            )


        relationships = []


        for (
            source_table,
            source_column,
            target_table,
            target_column
        ) in foreign_keys:

            if source_table == table_name:

                relationships.append(
                    f"{source_table}.{source_column} -> "
                    f"{target_table}.{target_column}"
                )

            elif target_table == table_name:

                relationships.append(
                    f"{source_table}.{source_column} -> "
                    f"{target_table}.{target_column}"
                )


        if relationships:

            lines.append(
                "Relationships:"
            )

            for relationship in relationships:

                lines.append(
                    f"- {relationship}"
                )


        documents[table_name] = "\n".join(lines)


    return documents


def retrieve_schema(
    question,
    top_k=3
):

    results = retrieve_tables(
        question,
        top_k=top_k
    )


    retrieved_names = [
        result["table"]
        for result in results
    ]


    expanded_names = expand_related_tables(
        retrieved_names
    )


    all_documents = get_table_documents()


    selected_documents = []


    for table_name in expanded_names:

        if table_name in all_documents:

            selected_documents.append(
                all_documents[table_name]
            )


    return "\n\n".join(
        selected_documents
    )