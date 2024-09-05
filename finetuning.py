import json
from setup import client

def generate_finetuning_data(schema, examples, output_file):
    """
    Generate fine-tuning data in JSONL format.
    
    :param schema: Dictionary containing schema details.
    :param examples: List of tuples with (query, completion) pairs.
    :param output_file: Path to the output JSONL file.
    """
    with open(output_file, 'w') as file:
        for query, completion in examples:
            data = {
                "prompt": f"Schema: {json.dumps(schema, indent=2)}\nQuery: {query}",
                "completion": completion
            }
            file.write(json.dumps(data) + '\n')

# Example schema | will be generated from DB setup
schema = {
    "tables": {
        "customers": {
            "columns": ["customer_id", "customer_name", "email"]
        },
        "orders": {
            "columns": ["order_id", "customer_id", "created_at"]
        },
        "order_items": {
            "columns": ["order_item_id", "order_id", "product_id", "quantity"]
        },
        "products": {
            "columns": ["product_id", "name", "price"]
        }
    },
    "relationships": {
        "customers_orders": {
            "type": "one_to_many",
            "from_table": "customers",
            "from_column": "customer_id",
            "to_table": "orders",
            "to_column": "customer_id"
        },
        "orders_order_items": {
            "type": "one_to_many",
            "from_table": "orders",
            "from_column": "order_id",
            "to_table": "order_items",
            "to_column": "order_id"
        },
        "products_order_items": {
            "type": "one_to_many",
            "from_table": "products",
            "from_column": "product_id",
            "to_table": "order_items",
            "to_column": "product_id"
        }
    }
}

# Example queries and completions  | will be generated from openAI models
examples = [
    ("How many times has the product 'kids baby cussions oil' been bought last week?", "SELECT COUNT(*) AS purchase_count FROM products p JOIN order_items oi ON p.product_id = oi.product_id JOIN orders o ON oi.order_id = o.order_id WHERE p.name = 'kids baby cussions oil' AND o.order_date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY);"),
    ("Show me the list of customers who bought 'Mens wallet' last week", "SELECT c.customer_id, c.customer_name FROM customers c JOIN orders o ON c.customer_id = o.customer_id JOIN order_items oi ON o.order_id = oi.order_id JOIN products p ON oi.product_id = p.product_id WHERE p.name = 'Mens wallet' AND o.order_date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY);"),
    ("I want to see the customers whose emails have a charity.co.ke work emails", "SELECT * FROM customers WHERE email LIKE '%@charity.co.ke';"),
    ("What is the total revenue from orders placed last month?", "SELECT SUM(p.price * oi.quantity) AS total_revenue FROM products p JOIN order_items oi ON p.product_id = oi.product_id JOIN orders o ON oi.order_id = o.order_id WHERE o.order_date >= DATE_FORMAT(CURDATE() - INTERVAL 1 MONTH, '%Y-%m-01') AND o.order_date < DATE_FORMAT(CURDATE(), '%Y-%m-01');"),
    ("How many distinct products were sold last week?", "SELECT COUNT(DISTINCT product_id) AS distinct_products_sold FROM order_items oi JOIN orders o ON oi.order_id = o.order_id WHERE o.order_date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY);"),
    ("Show me all orders placed in the last 30 days", "SELECT * FROM orders WHERE order_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY);"),
    ("Which customers bought more than 3 products in a single order?", "SELECT c.customer_name, o.order_id FROM customers c JOIN orders o ON c.customer_id = o.customer_id JOIN order_items oi ON o.order_id = oi.order_id GROUP BY c.customer_name, o.order_id HAVING COUNT(oi.product_id) > 3;"),
    ("List all products that have never been ordered", "SELECT p.name FROM products p LEFT JOIN order_items oi ON p.product_id = oi.product_id WHERE oi.order_id IS NULL;"),
    ("Show me the average order value per customer", "SELECT c.customer_name, AVG(oi.quantity * p.price) AS average_order_value FROM customers c JOIN orders o ON c.customer_id = o.customer_id JOIN order_items oi ON o.order_id = oi.order_id JOIN products p ON oi.product_id = p.product_id GROUP BY c.customer_name;"),
    ("Which products have been ordered more than 10 times?", "SELECT p.name, COUNT(*) AS order_count FROM products p JOIN order_items oi ON p.product_id = oi.product_id GROUP BY p.name HAVING order_count > 10;"),
    ("How many customers have placed an order?", "SELECT COUNT(DISTINCT customer_id) AS customer_count FROM orders;"),
    ("List all customers who have not placed an order", "SELECT c.customer_name FROM customers c LEFT JOIN orders o ON c.customer_id = o.customer_id WHERE o.order_id IS NULL;"),
    ("What is the total quantity of 'Laptop' sold?", "SELECT SUM(oi.quantity) AS total_quantity FROM products p JOIN order_items oi ON p.product_id = oi.product_id WHERE p.name = 'Laptop';"),
    ("Show me the most popular product", "SELECT p.name, COUNT(*) AS purchase_count FROM products p JOIN order_items oi ON p.product_id = oi.product_id GROUP BY p.name ORDER BY purchase_count DESC LIMIT 1;"),
    ("Which customers placed orders worth more than $500?", "SELECT c.customer_name, SUM(oi.quantity * p.price) AS total_spent FROM customers c JOIN orders o ON c.customer_id = o.customer_id JOIN order_items oi ON o.order_id = oi.order_id JOIN products p ON oi.product_id = p.product_id GROUP BY c.customer_name HAVING total_spent > 500;")
]


# Generate JSONL file
def create_finetuned_model():
    generate_finetuning_data(schema, examples, 'finetuning_data.jsonl')

    finetuning_file = client.files.create(
        file=open("finetuning_data.jsonl", "rb"),
        purpose="fine-tune"
    )


    finetuned_model = client.fine_tuning.jobs.create(
        training_file=finetuning_file.id, 
        model="davinci-002",
    )

    print("\nMODEL ID", finetuned_model.id)

    print("\nMODEL:", finetuned_model)

    print("\nFILE", finetuning_file.id)

    return finetuned_model.id 


# create_finetuned_model()
# res = client.fine_tuning.jobs.retrieve("ftjob-OoLUa7GSLczfk9IbDFxBkVRu")
# print(res.status, res.fine_tuned_model)

# example
# model id: ft:davinci-002:personal::A1x7KmkV

def load_schema(file_path='schema.json'):
    with open(file_path, 'r') as file:
        schema = json.load(file)
    return schema

schema = load_schema('schema_flip.json')
query = "List all assessments with repair amount more than KES 200,000"
completion = client.completions.create(
  model="ft:davinci-002:personal::A1x7KmkV",
  prompt=f"Prepare the correct SQL to retrieve records from the database using the provided question using the database schema: {schema}. \
    Only return one correct and precise SQL statement. Here is the question: " + query,
  max_tokens=300,  # Reduce max tokens to avoid repetition
  temperature=0,
  stop=[";"]
)

print(completion.choices[0].text)
print("\nUSAGE: ", completion.usage)


