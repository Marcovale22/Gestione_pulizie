import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "gestione.db")

_connection = None


def get_connection():
    global _connection
    if _connection is None:
        _connection = sqlite3.connect(DB_PATH)
        _connection.row_factory = sqlite3.Row
        _connection.execute("PRAGMA foreign_keys = ON;")  # IMPORTANTISSIMO in SQLite
    return _connection


def reset_db():
    """Cancella fisicamente il file DB e lo ricrea pulito."""
    global _connection
    if _connection is not None:
        _connection.close()
        _connection = None

    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    init_db()


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # --- CLIENTI ---
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

    # --- DIPENDENTI ---
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

    # --- SERVIZI ---
    # "prezzo_orario" -> sostituito con "prezzo_mensile"
    # campi extra utili: durata_default_ore, attivo
    cur.execute("""
        CREATE TABLE IF NOT EXISTS servizi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            descrizione TEXT,
            prezzo_mensile REAL,
            durata_default_ore REAL,
            attivo INTEGER NOT NULL DEFAULT 1
        );
    """)

    # --- INTERVENTI (istanze reali) ---
    # NIENTE dipendente_id qui: la relazione è N-N su interventi_dipendenti
    cur.execute("""
        CREATE TABLE IF NOT EXISTS interventi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            servizio_id INTEGER NOT NULL,
            data TEXT NOT NULL,        -- YYYY-MM-DD
            ora_inizio TEXT NOT NULL,  -- HH:MM
            durata_ore REAL,
            stato TEXT NOT NULL DEFAULT 'Programmato',
            note TEXT,
            ricorrente_id INTEGER,
            FOREIGN KEY (cliente_id) REFERENCES clienti(id) ON DELETE RESTRICT,
            FOREIGN KEY (servizio_id) REFERENCES servizi(id) ON DELETE RESTRICT,
            FOREIGN KEY (ricorrente_id) REFERENCES interventi_ricorrenti(id) ON DELETE SET NULL
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

    # --- INTERVENTI RICORRENTI (modello) ---
    cur.execute("""
        CREATE TABLE IF NOT EXISTS interventi_ricorrenti (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            servizio_id INTEGER NOT NULL,
            ora_inizio TEXT NOT NULL,
            durata_ore REAL,
            data_inizio TEXT,   -- YYYY-MM-DD (opzionale)
            data_fine TEXT,     -- YYYY-MM-DD (opzionale)
            attivo INTEGER NOT NULL DEFAULT 1,
            note TEXT,
            FOREIGN KEY (cliente_id) REFERENCES clienti(id) ON DELETE RESTRICT,
            FOREIGN KEY (servizio_id) REFERENCES servizi(id) ON DELETE RESTRICT
        );
    """)

    # --- Giorni della settimana per ricorrenti (0=Lun ... 6=Dom oppure come preferisci) ---
    cur.execute("""
        CREATE TABLE IF NOT EXISTS interventi_ricorrenti_giorni (
            ricorrente_id INTEGER NOT NULL,
            giorno_settimana INTEGER NOT NULL,
            PRIMARY KEY (ricorrente_id, giorno_settimana),
            FOREIGN KEY (ricorrente_id) REFERENCES interventi_ricorrenti(id) ON DELETE CASCADE
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

    # --- Indici utili (velocizzano calendario/ricerche) ---
    cur.execute("CREATE INDEX IF NOT EXISTS idx_interventi_data ON interventi(data);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_interventi_cliente ON interventi(cliente_id);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_interventi_servizio ON interventi(servizio_id);")

    conn.commit()
