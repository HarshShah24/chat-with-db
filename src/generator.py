from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate


# 1. Define the structure for the LLM output (remains the same)
class SQLResponse(BaseModel):
    sql: str = Field(description="The generated SQLite query")
    explanation: str = Field(description="A brief explanation of why this query was chosen")


def get_generator_chain(api_key=None):
    """
    Returns a structured LLM chain.
    If api_key is provided, it uses it; otherwise, it looks for OPENAI_API_KEY env var.
    """
    # 2. Initialize the Chat Model with the dynamic API Key
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        openai_api_key=api_key  # Pass the key here
    )

    # 3. Bind the Pydantic structure
    structured_llm = llm.with_structured_output(SQLResponse)

    # 4. Define the instructions
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a SQL expert. Use the provided schema to write a valid SQLite query. "
                   "Always use table aliases and join on primary/foreign keys."),
        ("human", "Schema:\n{schema}\n\nQuestion: {question}")
    ])

    return prompt | structured_llm