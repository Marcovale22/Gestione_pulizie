from database.database import get_connection


class Servizio:
    def __init__(self, id, nome, descrizione, prezzo_mensile):
        self.id = id
        self.nome = nome
        self.descrizione = descrizione
        self.prezzo_mensile = prezzo_mensile

    @staticmethod
    def all():
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, nome, descrizione, prezzo_mensile
            FROM servizi
            ORDER BY nome
        """)
        rows = cur.fetchall()

        servizi = []
        for r in rows:
            servizi.append(Servizio(
                id=r["id"],
                nome=r["nome"],
                descrizione=r["descrizione"],
                prezzo_mensile=r["prezzo_mensile"],
            ))
        return servizi

    @staticmethod
    def create(dati: dict):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO servizi (nome, descrizione, prezzo_mensile)
            VALUES (?, ?, ?)
        """, (
            dati["nome"],
            dati.get("descrizione"),
            dati.get("prezzo_mensile"),
        ))
        conn.commit()
        return cur.lastrowid

    @staticmethod
    def update(servizio_id: int, dati: dict):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE servizi
            SET nome = ?, descrizione = ?, prezzo_mensile = ?
            WHERE id = ?
        """, (
            dati["nome"],
            dati.get("descrizione"),
            dati.get("prezzo_mensile"),
            servizio_id
        ))
        conn.commit()

    @staticmethod
    def delete(servizio_id: int):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM servizi WHERE id = ?", (servizio_id,))
        conn.commit()
