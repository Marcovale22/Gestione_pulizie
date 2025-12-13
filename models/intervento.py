from database.database import get_connection


class Intervento:
    def __init__(self, id, cliente_id, servizio_id, dipendente_id, data, ora_inizio, durata_ore, stato, note):
        self.id = id
        self.cliente_id = cliente_id
        self.servizio_id = servizio_id
        self.dipendente_id = dipendente_id
        self.data = data
        self.ora_inizio = ora_inizio
        self.durata_ore = durata_ore
        self.stato = stato
        self.note = note

    @staticmethod
    def all():
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, cliente_id, servizio_id, dipendente_id,
                   data, ora_inizio, durata_ore, stato, note
            FROM interventi
            ORDER BY data DESC, ora_inizio DESC
        """)
        rows = cur.fetchall()

        out = []
        for r in rows:
            out.append(Intervento(
                id=r["id"],
                cliente_id=r["cliente_id"],
                servizio_id=r["servizio_id"],
                dipendente_id=r["dipendente_id"],
                data=r["data"],
                ora_inizio=r["ora_inizio"],
                durata_ore=r["durata_ore"],
                stato=r["stato"],
                note=r["note"],
            ))
        return out

    @staticmethod
    def create(dati: dict):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO interventi
                (cliente_id, servizio_id, dipendente_id, data, ora_inizio, durata_ore, stato, note)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            dati["cliente_id"],
            dati["servizio_id"],
            dati.get("dipendente_id"),
            dati["data"],
            dati["ora_inizio"],
            dati.get("durata_ore"),
            dati.get("stato", "Programmato"),
            dati.get("note"),
        ))
        conn.commit()
        return cur.lastrowid

    @staticmethod
    def update(intervento_id: int, dati: dict):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE interventi
            SET cliente_id = ?, servizio_id = ?, dipendente_id = ?,
                data = ?, ora_inizio = ?, durata_ore = ?, stato = ?, note = ?
            WHERE id = ?
        """, (
            dati["cliente_id"],
            dati["servizio_id"],
            dati.get("dipendente_id"),
            dati["data"],
            dati["ora_inizio"],
            dati.get("durata_ore"),
            dati.get("stato", "Programmato"),
            dati.get("note"),
            intervento_id
        ))
        conn.commit()

    @staticmethod
    def delete(intervento_id: int):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM interventi WHERE id = ?", (intervento_id,))
        conn.commit()
