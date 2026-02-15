from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import SKLearnVectorStore
from langchain_core.documents import Document


def create_vector_store(db, api_key=None):
    """
    Takes a LangChain SQLDatabase object and an optional API key.
    If no api_key is provided, it will look for the OPENAI_API_KEY env var.
    """
    # 1. Initialize embeddings with the provided key
    # If api_key is None, LangChain automatically looks for the environment variable
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=api_key
    )

    # 2. Extract schemas
    table_names = db.get_usable_table_names()
    documents = []

    for table in table_names:
        table_info = db.get_table_info(table_names=[table])
        doc = Document(
            page_content=table_info,
            metadata={"name": table}
        )
        documents.append(doc)

    # 3. Build vector store
    vector_db = SKLearnVectorStore.from_documents(
        documents=documents,
        embedding=embeddings
    )

    return vector_db