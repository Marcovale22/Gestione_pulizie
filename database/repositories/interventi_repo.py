from database.database import get_connection

def get_interventi_misti():
    conn = get_connection()
    cur = conn.cursor()

    sql = """
    -- SINGOLI (istanze reali)
    SELECT
      i.id AS id_ref,
      'SINGOLO' AS tipo,
      c.nome || ' ' || c.cognome AS cliente,
      s.nome AS servizio,
      COALESCE(GROUP_CONCAT(d.nome || ' ' || d.cognome, ', '), '-') AS dipendenti,
      i.data AS data,
      i.ora_inizio AS ora,
      COALESCE(i.durata_ore, '') AS durata,
      '-' AS giorni,
      i.stato AS stato,
      '-' AS periodo
    FROM interventi i
    JOIN clienti c ON c.id = i.cliente_id
    JOIN servizi s ON s.id = i.servizio_id
    LEFT JOIN interventi_dipendenti idp ON idp.intervento_id = i.id
    LEFT JOIN dipendenti d ON d.id = idp.dipendente_id
    GROUP BY i.id

    UNION ALL

    -- RICORRENTI (regole)
    SELECT
      r.id AS id_ref,
      'RICORRENTE' AS tipo,
      c.nome || ' ' || c.cognome AS cliente,
      s.nome AS servizio,
      COALESCE(GROUP_CONCAT(DISTINCT d.nome || ' ' || d.cognome), '-') AS dipendenti,
      '-' AS data,
      r.ora_inizio AS ora,
      COALESCE(r.durata_ore, '') AS durata,
      COALESCE(GROUP_CONCAT(DISTINCT rg.giorno_settimana), '-') AS giorni,
      CASE WHEN r.attivo=1 THEN 'Attivo' ELSE 'Sospeso' END AS stato,
      (COALESCE(r.data_inizio,'-') || ' → ' || COALESCE(r.data_fine,'-')) AS periodo
    FROM interventi_ricorrenti r
    JOIN clienti c ON c.id = r.cliente_id
    JOIN servizi s ON s.id = r.servizio_id
    LEFT JOIN interventi_ricorrenti_giorni rg ON rg.ricorrente_id = r.id
    LEFT JOIN ricorrenti_dipendenti rdp ON rdp.ricorrente_id = r.id
    LEFT JOIN dipendenti d ON d.id = rdp.dipendente_id
    GROUP BY r.id

    ORDER BY tipo DESC, data DESC, ora ASC;
    """

    cur.execute(sql)
    return cur.fetchall()


def get_intervento_by_id(intervento_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM interventi WHERE id = ?", (intervento_id,))
    return cur.fetchone()


def get_intervento_dipendenti_ids(intervento_id: int) -> list[int]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT dipendente_id
        FROM interventi_dipendenti
        WHERE intervento_id = ?
        ORDER BY dipendente_id
    """, (intervento_id,))
    return [row["dipendente_id"] for row in cur.fetchall()]


def set_intervento_dipendenti(intervento_id: int, dipendente_ids: list[int]):
    conn = get_connection()
    cur = conn.cursor()

    # reset
    cur.execute("DELETE FROM interventi_dipendenti WHERE intervento_id = ?", (intervento_id,))

    # insert nuovi
    for did in dipendente_ids:
        cur.execute("""
            INSERT OR IGNORE INTO interventi_dipendenti(intervento_id, dipendente_id)
            VALUES (?, ?)
        """, (intervento_id, did))

    conn.commit()


def create_intervento(dati: dict) -> int:
    """
    dati: cliente_id, servizio_id, data, ora_inizio, durata_ore, stato, note, dipendente_ids (lista)
    """
    conn = get_connection()
    cur = conn.cursor()

    dip_ids = dati.pop("dipendente_ids", [])  # tolgo dal dict

    cur.execute("""
        INSERT INTO interventi(cliente_id, servizio_id, data, ora_inizio, durata_ore, stato, note)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        dati["cliente_id"],
        dati["servizio_id"],
        dati["data"],
        dati["ora_inizio"],
        dati.get("durata_ore"),
        dati.get("stato", "Programmato"),
        dati.get("note"),
    ))

    intervento_id = cur.lastrowid
    conn.commit()

    # link dipendenti
    set_intervento_dipendenti(intervento_id, dip_ids)

    return intervento_id


def update_intervento(intervento_id: int, dati: dict):
    conn = get_connection()
    cur = conn.cursor()

    dip_ids = dati.pop("dipendente_ids", [])

    cur.execute("""
        UPDATE interventi
        SET cliente_id=?, servizio_id=?, data=?, ora_inizio=?, durata_ore=?, stato=?, note=?
        WHERE id=?
    """, (
        dati["cliente_id"],
        dati["servizio_id"],
        dati["data"],
        dati["ora_inizio"],
        dati.get("durata_ore"),
        dati.get("stato", "Programmato"),
        dati.get("note"),
        intervento_id
    ))
    conn.commit()

    set_intervento_dipendenti(intervento_id, dip_ids)


def delete_intervento(intervento_id: int):
    conn = get_connection()
    cur = conn.cursor()

    # cancella link (anche se con FK+CASCADE dovrebbe bastare)
    cur.execute("DELETE FROM interventi_dipendenti WHERE intervento_id = ?", (intervento_id,))
    cur.execute("DELETE FROM interventi WHERE id = ?", (intervento_id,))
    conn.commit()