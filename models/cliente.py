import sqlite3
from dataclasses import dataclass
from typing import List, Optional

from database.database import get_connection


@dataclass
class Cliente:
    id: int | None
    nome: str
    cognome: str
    telefono: str | None = None
    indirizzo: str | None = None
    email: str | None = None

    # ---------- CRUD ----------

    @staticmethod
    def all() -> List["Cliente"]:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM clienti ORDER BY cognome, nome;")
        rows = cur.fetchall()
        return [
            Cliente(
                id=row["id"],
                nome=row["nome"],
                cognome=row["cognome"],
                telefono=row["telefono"],
                indirizzo=row["indirizzo"],
                email=row["email"],
            )
            for row in rows
        ]

    @staticmethod
    def create(nome: str, cognome: str,
               telefono: str = "", indirizzo: str = "",
               email: str = "") -> "Cliente":
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO clienti (nome, cognome, telefono, indirizzo, email)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (nome, cognome, telefono, indirizzo, email),
        )
        conn.commit()
        new_id = cur.lastrowid
        return Cliente(new_id, nome, cognome, telefono, indirizzo, email)

    @staticmethod
    def get(client_id: int) -> Optional["Cliente"]:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM clienti WHERE id = ?;", (client_id,))
        row = cur.fetchone()
        if row is None:
            return None
        return Cliente(
            id=row["id"],
            nome=row["nome"],
            cognome=row["cognome"],
            telefono=row["telefono"],
            indirizzo=row["indirizzo"],
            email=row["email"],
        )

    def update(self):
        if self.id is None:
            raise ValueError("Cliente senza id, impossibile aggiornare")
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE clienti
            SET nome = ?, cognome = ?, telefono = ?, indirizzo = ?, email = ?
            WHERE id = ?
            """,
            (self.nome, self.cognome, self.telefono,
             self.indirizzo, self.email, self.id),
        )
        conn.commit()

    def delete(self):
        if self.id is None:
            return
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM clienti WHERE id = ?;", (self.id,))
        conn.commit()
