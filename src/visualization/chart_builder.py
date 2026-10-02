from numbers import Number


TIME_WORDS = {
    "trend",
    "over time",
    "daily",
    "day",
    "weekly",
    "week",
    "monthly",
    "month",
    "yearly",
    "year"
}


def _is_numeric_column(rows, index):

    values = [
        row[index]
        for row in rows
        if row[index] is not None
    ]

    if not values:
        return False

    return all(
        isinstance(value, Number)
        and not isinstance(value, bool)
        for value in values
    )


def _chart_value(value):

    if isinstance(value, Number):
        return float(value)

    return value


def build_chart(result, question, title=None):

    if not isinstance(result, dict):
        return None

    columns = result.get("columns", [])
    rows = result.get("rows", [])

    if len(columns) < 2 or len(rows) < 2:
        return None

    numeric_indices = [
        index
        for index in range(len(columns))
        if _is_numeric_column(rows, index)
    ]

    if not numeric_indices:
        return None

    non_numeric_indices = [
        index
        for index in range(len(columns))
        if index not in numeric_indices
    ]

    if non_numeric_indices:

        x_index = non_numeric_indices[0]

    else:

        x_index = 0

    y_indices = [
        index
        for index in numeric_indices
        if index != x_index
    ]

    if not y_indices:
        return None

    y_index = y_indices[0]

    question_lower = question.lower()

    chart_type = (
        "line"
        if any(
            word in question_lower
            for word in TIME_WORDS
        )
        else "bar"
    )

    chart_rows = [
        {
            columns[x_index]: _chart_value(
                row[x_index]
            ),
            columns[y_index]: _chart_value(
                row[y_index]
            )
        }
        for row in rows
    ]

    return {
        "type": chart_type,
        "x": columns[x_index],
        "y": columns[y_index],
        "title": title or (
            f"{columns[y_index]} by "
            f"{columns[x_index]}"
        ),
        "data": chart_rows
    }
