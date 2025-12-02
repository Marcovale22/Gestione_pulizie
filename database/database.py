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
    """Crea le tabelle se non esistono e inserisce dati di esempio."""
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

    # Se la tabella è vuota, inserisco alcuni clienti di esempio
    cur.execute("SELECT COUNT(*) AS c FROM clienti;")
    if cur.fetchone()["c"] == 0:
        cur.executemany("""
            INSERT INTO clienti (nome, cognome, telefono, indirizzo, email)
            VALUES (?, ?, ?, ?, ?);
        """, [
            ("Luigi",  "Bianchi", "3405618282", "Via Roma 2", "luigi.bianchi@example.com"),
            ("Anna",   "Verdi",   "3209876543", "Via Milano 10", "anna.verdi@example.com"),
        ])
        conn.commit()
