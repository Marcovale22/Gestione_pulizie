import unittest

class Cliente:
    def __init__(self, id, nome, telefono):
        self.id = id
        self.nome = nome
        self.telefono = telefono

    def __str__(self):
        return f"{self.id}-{self.nome}"

class ClienteTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cliente = Cliente(id=1, nome="Mario", telefono="3331234567")

    def test_nome(self):
        self.assertEqual(self.cliente.nome, "Mario")

    def test_telefono(self):
        self.assertEqual(self.cliente.telefono, "3331234567")

    def test_object_name_is_id_and_nome(self):
        self.assertEqual(str(self.cliente), "1-Mario")


if __name__ == "__main__":
    unittest.main()
