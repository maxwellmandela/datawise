## ⚠️ CAUTION

**Please Note:**  
This project is still in its early stages of development, and there’s a chance it may not function as expected on your machine at the moment. I'll be working on improvements, but consider this an experimental tool, and try to avoid any **CREATE** commands on a production database.

Additionally, **be extremely cautious** when using this code, as it generates and runs SQL queries directly on your database. Incorrect or unintended queries could modify or delete your data. It's essential to **double-check** the queries generated before execution.

Furthermore, to enable AI-driven query generation, portions of your database schema may be sent to OpenAI for processing. Ensure that no sensitive or private information is included in the schema before using the tool.

Only the schema is shared with openai models, not the data on your database(that is not shared). This is what makes it a cool project.

This is an exciting experiment, but please proceed carefully and with an understanding of the risks involved.

# DataWise BI Tool

**DataWise** is an AI-powered BI tool that helps users interact with relational databases using plain language queries. It generates SQL queries automatically and displays the results in a user-friendly interface, without needing any SQL expertise. The backbone of this project is [RAG](https://en.wikipedia.org/wiki/Retrieval-augmented_generation)

## Requirements

- Python 3.8+
- `pip` (Python package manager)

## Getting Started

Follow the steps below to set up and run the project locally.

### 1. Clone the Repository

```bash
git clone the-repo-url
cd datawise
```

### 2. Create a Virtual Environment

It's recommended to use a Python virtual environment to isolate dependencies.

```bash
python3 -m venv venv
```

### 3. Activate the Virtual Environment

For macOS/Linux:

```bash

source venv/bin/activate
```

For Windows:

```bash
    .\venv\Scripts\activate
```

### 4. Install Requirements

Install the necessary packages from the requirements.txt file.

```bash
pip install -r requirements.txt
```

### 5. Add Environment Variables

Make sure you configure the environment variables required for your database and API credentials. You can create a .env file in the project root with the following content:

```makefile

OPENAI_KEY=your-openai-api-key
HOST=localhost
DB_USER=admin
PASSWORD=password
DATABASE=datawise-db2
PORT=3306
```

### 6. Run the Application

Once the setup is complete, run the Streamlit app.

```bash
streamlit run app.py
```

### 7. Access the Application

After running the command, Streamlit will start the web app. Open the provided URL (e.g., http://localhost:8501) in your browser to access the tool.

#### Features

- Convert plain language questions into SQL queries.
- Query relational databases without SQL knowledge.
- Visualize query results in a tabular format.
- Configure database connections and API keys in the settings.

#### License

This project is licensed under the MIT License.
