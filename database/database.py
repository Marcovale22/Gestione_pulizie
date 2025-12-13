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

    # --- aggiunta colonna ricorrente_id se manca (SQLite safe) ---
    cur.execute("PRAGMA table_info(interventi);")
    cols = [row["name"] for row in cur.fetchall()]
    if "ricorrente_id" not in cols:
        cur.execute("ALTER TABLE interventi ADD COLUMN ricorrente_id INTEGER;")

    # --- Tabella INTERVENTI_RICORRENTI ---
    cur.execute("""
        CREATE TABLE IF NOT EXISTS interventi_ricorrenti (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            servizio_id INTEGER NOT NULL,
            ora_inizio TEXT NOT NULL,
            durata_ore REAL,
            attivo INTEGER NOT NULL DEFAULT 1,
            note TEXT,
            FOREIGN KEY (cliente_id) REFERENCES clienti(id),
            FOREIGN KEY (servizio_id) REFERENCES servizi(id)
        );
    """)

    # --- Tabella giorni ricorrenti ---
    cur.execute("""
        CREATE TABLE IF NOT EXISTS interventi_ricorrenti_giorni (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ricorrente_id INTEGER NOT NULL,
            giorno_settimana INTEGER NOT NULL,
            FOREIGN KEY (ricorrente_id) REFERENCES interventi_ricorrenti(id) ON DELETE CASCADE
        );
    """)

    # --- N-N dipendenti su interventi reali ---
    cur.execute("""
        CREATE TABLE IF NOT EXISTS interventi_dipendenti (
            intervento_id INTEGER NOT NULL,
            dipendente_id INTEGER NOT NULL,
            PRIMARY KEY (intervento_id, dipendente_id),
            FOREIGN KEY (intervento_id) REFERENCES interventi(id) ON DELETE CASCADE,
            FOREIGN KEY (dipendente_id) REFERENCES dipendenti(id) ON DELETE CASCADE
        );
    """)

    # --- N-N dipendenti su ricorrenti ---
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ricorrenti_dipendenti (
            ricorrente_id INTEGER NOT NULL,
            dipendente_id INTEGER NOT NULL,
            PRIMARY KEY (ricorrente_id, dipendente_id),
            FOREIGN KEY (ricorrente_id) REFERENCES interventi_ricorrenti(id) ON DELETE CASCADE,
            FOREIGN KEY (dipendente_id) REFERENCES dipendenti(id) ON DELETE CASCADE
        );
    """)


    conn.commit()


