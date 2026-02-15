import streamlit as st
import pandas as pd
from src.database import init_db
from src.embedding import create_vector_store
from src.generator import get_generator_chain
import os

# --- Sidebar Configuration ---
with st.sidebar:
    st.title("Settings")
    # Taking the API Key as input
    user_openai_api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        help="Enter your OpenAI API key to start querying."
    )

    st.info("Your key is used only for this session and is not stored.")

# --- Logic to check for the key ---
if not user_openai_api_key:
    st.warning("Please enter your OpenAI API key in the sidebar to continue.")
    st.stop()  # Stops the rest of the app from running until key is provided
else:
    # Set the environment variable for LangChain/OpenAI to find
    os.environ["OPENAI_API_KEY"] = user_openai_api_key

# --- Page Config & Styling ---
st.set_page_config(page_title="SQL Chat Assistant", page_icon="📊", layout="wide")
st.title("📊 Chat with your SQL Database")
st.markdown("Ask questions in plain English, and I'll generate and execute the SQL for you.")


# --- Initialization (Cached to prevent re-loading on every click) ---
@st.cache_resource
def setup_backend(api_key):
    # Set key before initializing anything else
    os.environ["OPENAI_API_KEY"] = api_key

    db, engine = init_db("data/Chinook.db")
    vector_db = create_vector_store(db,api_key)
    chain = get_generator_chain(api_key)
    return db, engine, vector_db, chain


# Now call it using the sidebar value
db, engine, vector_db, chain = setup_backend(user_openai_api_key)

# --- Chat History Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Display Chat History ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "df" in message:
            st.dataframe(message["df"])

# --- Chat Input ---
if prompt := st.chat_input("How many tracks are in each genre?"):
    # 1. Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Generate Assistant Response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Retrieval
                relevant_docs = vector_db.similarity_search(prompt, k=3)
                context_schema = "\n\n".join([doc.page_content for doc in relevant_docs])

                # Generation
                response = chain.invoke({"schema": context_schema, "question": prompt})

                # Execution
                df = pd.read_sql(response.sql, engine)

                # Display results
                full_response = f"**SQL Query:**\n```sql\n{response.sql}\n```\n\n**Explanation:** {response.explanation}"
                st.markdown(full_response)
                st.dataframe(df)

                # Save to history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": full_response,
                    "df": df
                })
            except Exception as e:
                error_msg = f"❌ Error: {str(e)}"
                st.error(error_msg)