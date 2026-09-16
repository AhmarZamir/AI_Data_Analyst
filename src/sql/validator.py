from sqlglot import parse, exp
from sqlglot.errors import ParseError


ALLOWED_TABLES = {
    "customers",
    "products",
    "orders",
    "order_items",
    "payments"
}


FORBIDDEN_TYPES = (
    exp.Delete,
    exp.Update,
    exp.Insert,
    exp.Drop,
    exp.Create,
    exp.Alter
)


def validate_sql(query):

    try:

        statements = parse(
            query,
            read="postgres"
        )

    except ParseError as error:

        return False, f"Invalid SQL: {error}"


    if len(statements) != 1:

        return False, "Only one SQL statement is allowed."


    parsed_query = statements[0]


    for forbidden_type in FORBIDDEN_TYPES:

        if parsed_query.find(forbidden_type):

            return (
                False,
                f"Blocked SQL operation: {forbidden_type.__name__}"
            )


    if not parsed_query.find(exp.Select):

        return False, "Only SELECT queries are allowed."


    tables = parsed_query.find_all(
        exp.Table
    )


    for table in tables:

        table_name = table.name

        if table_name not in ALLOWED_TABLES:

            return (
                False,
                f"Access to table '{table_name}' is not allowed."
            )


    return True, "Query is safe."