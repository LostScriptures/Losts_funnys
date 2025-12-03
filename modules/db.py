from pathlib import Path
import sqlite3

def get_db_files() -> list[Path]:
    """Retrieve a list of database file names"""
    db_path = Path(__file__).parent.parent
    db_files = [f for f in db_path.glob("*.db")]
    return db_files

def connect_to_db(db_name: str) -> sqlite3.Connection:
    """Establish a connection to the specified SQLite database"""
    db_path = Path(__file__).parent.parent / db_name
    connection = sqlite3.connect(db_path)
    return connection

def close_db_connection(connection: sqlite3.Connection) -> None:
    """Close the given database connection"""
    if connection:
        connection.close()

def execute_query(connection: sqlite3.Connection, query: str) -> list[tuple]:
    """Execute a SQL query and return the results"""
    cursor = connection.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    return results

