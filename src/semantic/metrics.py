BUSINESS_METRICS = {

    "revenue": {
        "description": "Total successfully completed payments",
        "tables": ["payments"],
        "definition": (
            "SUM(payments.amount) "
            "WHERE payments.payment_status = 'completed'"
        )
    },

    "new customer": {
        "description": (
            "A customer whose account was created "
            "during the requested period"
        ),
        "tables": ["customers"],
        "definition": (
            "Count customers using customers.created_at "
            "inside the requested date range"
        )
    },

    "customer": {
        "description": "A unique record in the customers table",
        "tables": ["customers"],
        "definition": (
            "customers.customer_id represents one customer"
        )
    },

    "completed order": {
        "description": "An order successfully completed",
        "tables": ["orders"],
        "definition": (
            "orders.status = 'completed'"
        )
    },

    "pending order": {
        "description": "An order that is still pending",
        "tables": ["orders"],
        "definition": (
            "orders.status = 'pending'"
        )
    },

    "order count": {
        "description": "Total number of orders",
        "tables": ["orders"],
        "definition": (
            "COUNT(orders.order_id)"
        )
    },

    "gross sales": {
        "description": (
            "Total value of items ordered before payment filtering"
        ),
        "tables": ["order_items"],
        "definition": (
            "SUM(order_items.quantity * order_items.unit_price)"
        )
    },

    "completed order count": {

    "description": (
        "Number of successfully completed orders"
    ),

    "tables": [
        "orders"
    ],

    "definition": (
        "COUNT(orders.order_id) "
        "WHERE orders.status = 'completed'"
    )
},

    "average order value": {
        "description": (
            "Average completed revenue per completed order"
        ),
        "tables": [
            "orders",
            "payments"
        ],
        "definition": (
            "Total completed payment amount divided by "
            "number of completed orders"
        )
    },

    "customer growth": {
        "description": (
            "Percentage change in new customers "
            "between two periods"
        ),
        "tables": ["customers"],
        "definition": (
            "(current new customers - previous new customers) "
            "/ previous new customers * 100"
        )
    }
}

def format_business_metrics():

    lines = []

    for name, metric in BUSINESS_METRICS.items():

        lines.append(
            f"Metric: {name}"
        )

        lines.append(
            f"Description: {metric['description']}"
        )

        lines.append(
            f"Definition: {metric['definition']}"
        )

        lines.append(
            f"Relevant tables: {', '.join(metric['tables'])}"
        )

        lines.append("")

    return "\n".join(lines)