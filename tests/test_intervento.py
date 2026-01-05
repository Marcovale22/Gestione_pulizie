import unittest
from datetime import date, timedelta

def genera_date_ricorrenze(data_inizio: date, fine_contratto: date, ogni_giorni: int):
    dates = []
    d = data_inizio
    while d <= fine_contratto:
        dates.append(d)
        d += timedelta(days=ogni_giorni)
    return dates

class InterventoRicorrenteTestCase(unittest.TestCase):
    def test_generazione_ricorrenze(self):
        start = date(2026, 1, 1)
        end = date(2026, 1, 8)
        dates = genera_date_ricorrenze(start, end, 7)
        self.assertEqual(dates, [date(2026, 1, 1), date(2026, 1, 8)])

if __name__ == "__main__":
    unittest.main()
