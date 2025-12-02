import os
import sqlite3

# Percorso del file .db (database/gestione.db)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "gestione.db")

_connection = None


def get_connection():
    """Ritorna una connessione singleton al DB SQLite."""
    global _connection
    if _connection is None:
        _connection = sqlite3.connect(DB_PATH)
        _connection.row_factory = sqlite3.Row   # per avere dizionari
    return _connection


def init_db():
    """Crea le tabelle se non esistono."""
    conn = get_connection()
    cur = conn.cursor()

    # Tabella CLIENTI
    cur.execute("""
        CREATE TABLE IF NOT EXISTS clienti (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cognome TEXT NOT NULL,
            telefono TEXT,
            indirizzo TEXT,
            email TEXT
        );
    """)

    conn.commit()

    cur.execute("SELECT COUNT(*) AS c FROM clienti;")
    if cur.fetchone()["c"] == 0:
        cur.execute("""
            UPDATE INTO clienti (nome, cognome, telefono, indirizzo, email)
            VALUES ('Mario', 'Rossi', '3331234567', 'Via Roma 1', 'mario.rossi@example.com')
            Where nome = Mario;
        """)
        conn.commit()
