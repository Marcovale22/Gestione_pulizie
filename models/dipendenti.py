from database.database import get_connection


class Dipendente:
    def __init__(self, id, nome, cognome, telefono, email,
                 mansione, ore_settimanali, stipendio, scadenza_contratto):
        self.id = id
        self.nome = nome
        self.cognome = cognome
        self.telefono = telefono
        self.email = email
        self.mansione = mansione
        self.ore_settimanali = ore_settimanali
        self.stipendio = stipendio
        self.scadenza_contratto = scadenza_contratto

    # ---------------------------------------------------------
    #  TUTTI I DIPENDENTI
    # ---------------------------------------------------------
    @staticmethod
    def all():
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, nome, cognome, telefono, email,
                   mansione, ore_settimanali, stipendio, scadenza_contratto
            FROM dipendenti
            ORDER BY cognome, nome
        """)
        records = cur.fetchall()

        dipendenti = []
        for r in records:
            dip = Dipendente(
                id=r["id"],
                nome=r["nome"],
                cognome=r["cognome"],
                telefono=r["telefono"],
                email=r["email"],
                mansione=r["mansione"],
                ore_settimanali=r["ore_settimanali"],
                stipendio=r["stipendio"],
                scadenza_contratto=r["scadenza_contratto"],
            )
            dipendenti.append(dip)

        return dipendenti

    # ---------------------------------------------------------
    #  GET SINGOLO
    # ---------------------------------------------------------
    @staticmethod
    def get(id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, nome, cognome, telefono, email,
                   mansione, ore_settimanali, stipendio, scadenza_contratto
            FROM dipendenti
            WHERE id = ?
        """, (id,))
        r = cur.fetchone()

        if r is None:
            return None

        return Dipendente(
            id=r["id"],
            nome=r["nome"],
            cognome=r["cognome"],
            telefono=r["telefono"],
            email=r["email"],
            mansione=r["mansione"],
            ore_settimanali=r["ore_settimanali"],
            stipendio=r["stipendio"],
            scadenza_contratto=r["scadenza_contratto"],
        )

    # ---------------------------------------------------------
    #  CREATE
    # ---------------------------------------------------------
    @staticmethod
    def create(dati):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO dipendenti
                (nome, cognome, telefono, email, mansione,
                 ore_settimanali, stipendio, scadenza_contratto)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            dati["nome"],
            dati["cognome"],
            dati.get("telefono"),
            dati.get("email"),
            dati.get("mansione"),
            dati.get("ore_settimanali"),
            dati.get("stipendio"),
            dati.get("scadenza_contratto"),
        ))
        conn.commit()
        return cur.lastrowid

    # ---------------------------------------------------------
    #  UPDATE
    # ---------------------------------------------------------
    @staticmethod
    def update(id, dati):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE dipendenti
            SET nome = ?, cognome = ?, telefono = ?, email = ?,
                mansione = ?, ore_settimanali = ?, stipendio = ?, scadenza_contratto = ?
            WHERE id = ?
        """, (
            dati["nome"],
            dati["cognome"],
            dati.get("telefono"),
            dati.get("email"),
            dati.get("mansione"),
            dati.get("ore_settimanali"),
            dati.get("stipendio"),
            dati.get("scadenza_contratto"),
            id
        ))
        conn.commit()

    # ---------------------------------------------------------
    #  DELETE
    # ---------------------------------------------------------
    @staticmethod
    def delete(id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM dipendenti WHERE id = ?", (id,))
        conn.commit()
