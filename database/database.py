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

    # --- Tabella CLIENTI ---
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

    # --- Tabella DIPENDENTI ---
    cur.execute("""
        CREATE TABLE IF NOT EXISTS dipendenti (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cognome TEXT NOT NULL,
            telefono TEXT,
            email TEXT,
            mansione TEXT,
            ore_settimanali INTEGER,
            stipendio REAL,
            scadenza_contratto TEXT
        );
    """)

    # --- Tabella SERVIZI ---
    cur.execute("""
        CREATE TABLE IF NOT EXISTS servizi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            descrizione TEXT,
            prezzo_orario REAL
        );
    """)

    # --- Tabella INTERVENTI ---
    cur.execute("""
        CREATE TABLE IF NOT EXISTS interventi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            servizio_id INTEGER NOT NULL,
            dipendente_id INTEGER,                 -- può essere NULL
            data TEXT NOT NULL,                    -- 'YYYY-MM-DD'
            ora_inizio TEXT NOT NULL,              -- 'HH:MM'
            durata_ore REAL,                       -- es: 1.5
            stato TEXT NOT NULL DEFAULT 'Programmato',
            note TEXT
        );
    """)


    conn.commit()


