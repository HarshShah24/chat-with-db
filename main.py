import os
import pandas as pd
from dotenv import load_dotenv
from src.database import init_db
from src.embedding import create_vector_store
from src.generator import get_generator_chain


def main():
    # 1. Load environment variables (API Keys)
    load_dotenv()

    # 2. Initialize components
    print("--- Initializing Text-to-SQL System ---")
    db, engine = init_db("data/Chinook.db")
    vector_db = create_vector_store(db)
    structured_chain = get_generator_chain()

    print("✅ System Ready. Type 'exit' to quit.\n")

    while True:
        # 3. Get User Input
        user_question = input("SQL Assistant> ")
        if user_question.lower() in ['exit', 'quit']:
            break

        try:
            # 4. Step 1: Vector Search (Context Retrieval)
            relevant_docs = vector_db.similarity_search(user_question, k=3)
            context_schema = "\n\n".join([doc.page_content for doc in relevant_docs])

            # 5. Step 2: Generate SQL (LLM Reasoning)
            response = structured_chain.invoke({
                "schema": context_schema,
                "question": user_question
            })

            print(f"\n[Generated SQL]:\n{response.sql}\n")
            print(f"[Explanation]: {response.explanation}\n")

            # 6. Step 3: Execute (Database Interaction)
            df = pd.read_sql(response.sql, engine)

            print("[Results]:")
            if df.empty:
                print("No data found for this query.")
            else:
                print(df.to_string(index=False))
            print("-" * 30 + "\n")

        except Exception as e:
            print(f"❌ Error: {e}\n")


if __name__ == "__main__":
    main()