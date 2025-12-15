from __future__ import annotations
from datetime import date, datetime, timedelta
from typing import List, Optional

from database.database import get_connection
from database.repositories.interventi_repo import set_intervento_dipendenti

def _fine_anno(d: date) -> date:
    return date(d.year, 12, 31)

def _today_str() -> str:
    return date.today().strftime("%Y-%m-%d")

# convenzione: 1=Lun ... 7=Dom
def _to_db_dow(py_weekday: int) -> int:
    # python: Monday=0 ... Sunday=6
    return py_weekday + 1


def get_ricorrente_by_id(ricorrente_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM interventi_ricorrenti WHERE id=?", (ricorrente_id,))
    return cur.fetchone()


def get_ricorrente_giorni(ricorrente_id: int) -> List[int]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT giorno_settimana
        FROM interventi_ricorrenti_giorni
        WHERE ricorrente_id=?
        ORDER BY giorno_settimana
    """, (ricorrente_id,))
    return [row["giorno_settimana"] for row in cur.fetchall()]


def get_ricorrente_dipendenti_ids(ricorrente_id: int) -> List[int]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT dipendente_id
        FROM ricorrenti_dipendenti
        WHERE ricorrente_id=?
        ORDER BY dipendente_id
    """, (ricorrente_id,))
    return [row["dipendente_id"] for row in cur.fetchall()]


def set_ricorrente_giorni(ricorrente_id: int, giorni: List[int]):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM interventi_ricorrenti_giorni WHERE ricorrente_id=?", (ricorrente_id,))
    for g in sorted(set(giorni)):
        cur.execute("""
            INSERT INTO interventi_ricorrenti_giorni(ricorrente_id, giorno_settimana)
            VALUES (?, ?)
        """, (ricorrente_id, int(g)))
    conn.commit()


def set_ricorrente_dipendenti(ricorrente_id: int, dipendente_ids: List[int]):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM ricorrenti_dipendenti WHERE ricorrente_id=?", (ricorrente_id,))
    for did in sorted(set(dipendente_ids)):
        cur.execute("""
            INSERT OR IGNORE INTO ricorrenti_dipendenti(ricorrente_id, dipendente_id)
            VALUES (?, ?)
        """, (ricorrente_id, int(did)))
    conn.commit()


def create_ricorrente(dati: dict) -> int:
    conn = get_connection()
    cur = conn.cursor()

    giorni = dati.pop("giorni_settimana", [])
    dip_ids = dati.pop("dipendente_ids", [])

    # default: valido da oggi fino al 31/12
    start = date.today()
    data_inizio = dati.get("data_inizio") or start.strftime("%Y-%m-%d")
    data_fine = dati.get("data_fine") or _fine_anno(start).strftime("%Y-%m-%d")

    cur.execute("""
        INSERT INTO interventi_ricorrenti(
            cliente_id, servizio_id, ora_inizio, durata_ore, attivo, note, data_inizio, data_fine
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        dati["cliente_id"],
        dati["servizio_id"],
        dati["ora_inizio"],
        dati.get("durata_ore"),
        1 if dati.get("attivo", True) else 0,
        dati.get("note"),
        data_inizio,
        data_fine
    ))
    ric_id = cur.lastrowid
    conn.commit()

    set_ricorrente_giorni(ric_id, giorni)
    set_ricorrente_dipendenti(ric_id, dip_ids)

    return ric_id



def update_ricorrente(ricorrente_id: int, dati: dict):
    conn = get_connection()
    cur = conn.cursor()

    giorni = dati.pop("giorni_settimana", [])
    dip_ids = dati.pop("dipendente_ids", [])

    # se non arrivano, non le tocchiamo
    r = get_ricorrente_by_id(ricorrente_id)
    if r is None:
        return

    data_inizio = dati.get("data_inizio") or r["data_inizio"] or _today_str()
    data_fine = dati.get("data_fine") or r["data_fine"] or _fine_anno(date.today()).strftime("%Y-%m-%d")

    cur.execute("""
        UPDATE interventi_ricorrenti
        SET cliente_id=?, servizio_id=?, ora_inizio=?, durata_ore=?, attivo=?, note=?, data_inizio=?, data_fine=?
        WHERE id=?
    """, (
        dati["cliente_id"],
        dati["servizio_id"],
        dati["ora_inizio"],
        dati.get("durata_ore"),
        1 if dati.get("attivo", True) else 0,
        dati.get("note"),
        data_inizio,
        data_fine,
        ricorrente_id
    ))
    conn.commit()

    set_ricorrente_giorni(ricorrente_id, giorni)
    set_ricorrente_dipendenti(ricorrente_id, dip_ids)


def delete_ricorrente(ricorrente_id: int):
    conn = get_connection()
    cur = conn.cursor()
    # cascata su giorni e ricorrenti_dipendenti (se hai FK + ON DELETE CASCADE)
    cur.execute("DELETE FROM interventi_ricorrenti WHERE id=?", (ricorrente_id,))
    conn.commit()


def rinnova_ricorrenti_scaduti():
    """
    Se un ricorrente è attivo e la sua data_fine è passata,
    estende data_fine al 31/12 dell'anno corrente.
    """
    conn = get_connection()
    cur = conn.cursor()

    today = date.today()
    today_str = today.strftime("%Y-%m-%d")
    fine_anno_str = _fine_anno(today).strftime("%Y-%m-%d")

    cur.execute("""
        UPDATE interventi_ricorrenti
        SET data_fine = ?
        WHERE attivo = 1
          AND data_fine IS NOT NULL
          AND data_fine < ?
    """, (fine_anno_str, today_str))

    conn.commit()
