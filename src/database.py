import os
import requests
from sqlalchemy import create_engine
from langchain_community.utilities import SQLDatabase


def init_db(db_path="data/Chinook.db"):
    """
    Downloads the Chinook database if it doesn't exist
    and returns a LangChain SQLDatabase object.
    """
    # 1. Download the database into the /data folder if missing
    db_url = "https://github.com/lerocha/chinook-database/raw/master/ChinookDatabase/DataSources/Chinook_Sqlite.sqlite"

    if not os.path.exists(db_path):
        print(f"Downloading database to {db_path}...")
        response = requests.get(db_url)
        with open(db_path, "wb") as f:
            f.write(response.content)

    # 2. Create the SQLAlchemy engine
    # Note: SQLite uses three slashes for relative paths
    engine = create_engine(f"sqlite:///{db_path}")

    # 3. Return the LangChain SQLDatabase wrapper
    return SQLDatabase(engine), engine


if __name__ == "__main__":
    # Test the connection
    db, engine = init_db()
    print("Connection Successful!")
    print("Tables:", db.get_usable_table_names())