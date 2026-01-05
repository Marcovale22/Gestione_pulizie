import unittest
import sqlite3

class ClienteDAO:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def create(self, nome: str, telefono: str) -> int:
        cur = self.conn.execute(
            "INSERT INTO clienti(nome, telefono) VALUES (?, ?)",
            (nome, telefono),
        )
        self.conn.commit()
        return cur.lastrowid

    def get_by_id(self, id_: int):
        cur = self.conn.execute("SELECT id, nome, telefono FROM clienti WHERE id=?", (id_,))
        row = cur.fetchone()
        return row  # (id, nome, telefono) o None


class ClienteDAOTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.conn = sqlite3.connect(":memory:")
        cls.conn.execute("""
            CREATE TABLE clienti(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                telefono TEXT NOT NULL
            )
        """)
        cls.dao = ClienteDAO(cls.conn)

        cls.cliente_id = cls.dao.create("Mario", "3331234567")

    def test_create_cliente(self):
        self.assertIsInstance(self.cliente_id, int)
        self.assertGreater(self.cliente_id, 0)

    def test_get_by_id(self):
        row = self.dao.get_by_id(self.cliente_id)
        self.assertIsNotNone(row)
        self.assertEqual(row[1], "Mario")
        self.assertEqual(row[2], "3331234567")


if __name__ == "__main__":
    unittest.main()
