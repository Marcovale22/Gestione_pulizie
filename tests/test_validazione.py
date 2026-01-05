import unittest

def validate_cliente(nome: str, telefono: str):
    if not nome or not nome.strip():
        return False, "Nome obbligatorio"
    if not telefono or not telefono.strip():
        return False, "Telefono obbligatorio"
    return True, ""

class ValidazioneClienteTestCase(unittest.TestCase):
    def test_nome_obbligatorio(self):
        ok, err = validate_cliente("", "333")
        self.assertFalse(ok)
        self.assertIn("nome", err.lower())

    def test_telefono_obbligatorio(self):
        ok, err = validate_cliente("Mario", "")
        self.assertFalse(ok)
        self.assertIn("telefono", err.lower())

    def test_cliente_valido(self):
        ok, err = validate_cliente("Mario", "333")
        self.assertTrue(ok)
        self.assertEqual(err, "")

if __name__ == "__main__":
    unittest.main()
