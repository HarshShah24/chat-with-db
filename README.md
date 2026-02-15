🤖Text-to-SQL Research POC
Natural Language to SQLite using LangChain, OpenAI, and Vector Retrieval.

This project demonstrates a sophisticated pipeline that converts plain English questions into valid SQLite queries. Unlike basic implementations, this POC uses Dynamic Schema Retrieval to handle large databases efficiently without hitting LLM token limits.

🌟 Key Features
🔍 RAG-Enhanced Schema Selection: Instead of sending the entire database schema to the LLM, we use an in-memory SKLearnVectorStore to inject only the most relevant table definitions.

🛠 Self-Correction Loop: Automatically detects SQL execution errors and prompts the LLM to "fix" the query based on the traceback.

🏗 Structured Output: Uses Pydantic to enforce a strict JSON schema, ensuring the LLM returns both the sql and an explanation.

📊 Automatic Visualization: Seamlessly executes generated SQL and renders results using Pandas for immediate data inspection.

📂 Project Structure

├── data/               # Contains Chinook.db (SQLite)
├── notebooks/          # Original development experiments
├── src/
│   ├── database.py     # SQLAlchemy connection & DB utilities
│   ├── embedding.py    # Vector store & document processing
│   └── generator.py    # LLM logic & structured output chains
├── .env                # API Keys (Excluded from Git)
├── main.py             # Integration script (The "Main" Entry)
└── requirements.txt    # Project dependencies

🧠 Technical Workflow

Step,Component,Action
1. Indexing,OpenAIEmbeddings,Table DDLs are converted to vectors and stored in SKLearnVectorStore.
2. Retrieval,Similarity Search,Filters the top k tables relevant to the user's natural language question.
3. Generation,gpt-4o-mini,Prompted with the question + retrieved schema to produce a Pydantic object.
4. Execution,SQLAlchemy,The SQL is executed against Chinook.db.
5. Correction,Python Retry,"If execution fails, the error message is fed back to the LLM for one-shot correction."

📝 Example Usage
User Input: > "Who are the top 5 customers by total spending?"

System Response:

Logic: Joins Customer and Invoice tables, groups by customer ID, and sums the Total.

SQL: SELECT c.FirstName, c.LastName, SUM(i.Total) FROM Customer c JOIN ...