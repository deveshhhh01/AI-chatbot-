import sqlite3
from pathlib import Path
from contextlib import contextmanager
from backend.app.core.config import settings
from backend.app.core.logging import logger


def init_db():
    db_path = Path(settings.SQLITE_DB_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Conversations table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT UNIQUE NOT NULL,
        title TEXT DEFAULT 'New Real Estate Chat',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Messages table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        sources_json TEXT DEFAULT '[]',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES conversations(session_id)
    );
    """)

    # Scraped projects metadata table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scraped_projects (
        id TEXT PRIMARY KEY,
        source TEXT NOT NULL,
        project_name TEXT NOT NULL,
        country TEXT,
        city TEXT,
        property_type TEXT,
        price_amount REAL,
        currency TEXT,
        source_url TEXT UNIQUE,
        data_json TEXT NOT NULL,
        scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Ingestion run history table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ingestion_runs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id TEXT UNIQUE NOT NULL,
        status TEXT NOT NULL,
        started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        finished_at TIMESTAMP,
        darglobal_count INTEGER DEFAULT 0,
        wasalt_count INTEGER DEFAULT 0,
        total_chunks INTEGER DEFAULT 0,
        error_message TEXT
    );
    """)

    conn.commit()
    conn.close()
    logger.info("SQLite database initialized at: %s", db_path)


@contextmanager
def get_db():
    db_path = Path(settings.SQLITE_DB_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
