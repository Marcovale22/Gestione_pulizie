import re

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHeaderView, QAbstractItemView, QTableWidgetItem, QMessageBox
from datetime import datetime, date


from dialogs.intervento_dialog import InterventoDialog
from database.repositories.interventi_repo import (
    get_interventi_misti,
    get_intervento_by_id,
    get_intervento_dipendenti_ids,
    create_intervento,
    update_intervento,
    delete_intervento
)
from dialogs.ricorrente_dialog import RicorrenteDialog
from database.repositories.ricorrenti_repo import (
    get_ricorrente_by_id, get_ricorrente_giorni, get_ricorrente_dipendenti_ids,
    create_ricorrente, update_ricorrente, delete_ricorrente, rinnova_ricorrenti_scaduti
)


class InterventiSection:
    def __init__(self, ui):
        self.ui = ui
        self.setup_table()
        self.setup_signals()
        rinnova_ricorrenti_scaduti()
        self.load_interventi()

        self.ui.btnInterventiModifica.setEnabled(False)
        self.ui.btnInterventiElimina.setEnabled(False)

    def setup_table(self):
        table = self.ui.tableInterventi

        table.setColumnCount(11)
        table.setHorizontalHeaderLabels([
            "ID_REF", "TIPO", "Cliente", "Servizio", "Dipendenti",
            "Data", "Ora", "Durata", "Giorni", "Stato", "Periodo"
        ])
        table.setColumnHidden(0, True)
        table.setColumnHidden(1, True)

        header = table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

        table.setAlternatingRowColors(True)
        table.verticalHeader().setVisible(False)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        table.setShowGrid(True)
        table.setWordWrap(False)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        table.setStyleSheet(self.ui.tableClienti.styleSheet())

        table.setColumnWidth(2, 200)  # Cliente
        table.setColumnWidth(3, 160)  # Servizio
        table.setColumnWidth(4, 220)  # Dipendenti
        table.setColumnWidth(10, 220)  # Periodo
    def setup_signals(self):
        self.ui.btnInterventiAggiungi.clicked.connect(self.aggiungi_intervento)
        self.ui.btnInterventiModifica.clicked.connect(self.modifica_intervento)
        self.ui.btnInterventiElimina.clicked.connect(self.elimina_intervento)

        self.ui.tableInterventi.itemSelectionChanged.connect(self.on_selection_changed)

    def format_giorni(self, csv_nums: str) -> str:
        if not csv_nums or str(csv_nums).strip() in ("-", ""):
            return "-"

        GIORNI_MAP = {1: "Lun", 2: "Mar", 3: "Mer", 4: "Gio", 5: "Ven", 6: "Sab", 7: "Dom"}
        parts = [p.strip() for p in str(csv_nums).split(",")]
        nums = sorted({int(p) for p in parts if p.isdigit() and int(p) in GIORNI_MAP})
        return ", ".join(GIORNI_MAP[n] for n in nums) if nums else "-"



    def format_data(self, value) -> str:
        if value is None:
            return "-"

        # se è già un date/datetime
        if isinstance(value, (date, datetime)):
            return value.strftime("%d-%m-%Y")

        s = str(value).strip()
        if not s or s == "-":
            return "-"

        # prende solo la parte data se arriva "YYYY-MM-DD HH:MM:SS"
        s = s[:10]

        try:
            return datetime.strptime(s, "%Y-%m-%d").strftime("%d-%m-%Y")
        except ValueError:
            return str(value)  # fallback

    def format_durata_hhmm(self, durata_ore) -> str:
        if durata_ore is None or str(durata_ore).strip() in ("", "-"):
            return "-"

        try:
            total_min = int(round(float(durata_ore) * 60))
            h = total_min // 60
            m = total_min % 60
            return f"{h:02d}:{m:02d}"
        except:
            return "-"

    def format_periodo(self, periodo: str) -> str:
        if not periodo:
            return "-"

        s = str(periodo).strip()
        if not s or s == "-":
            return "-"

        # Estrae 2 date in formato YYYY-MM-DD da qualunque stringa
        dates = re.findall(r"\d{4}-\d{2}-\d{2}", s)
        if len(dates) >= 2:
            return f"{self.format_data(dates[0])} → {self.format_data(dates[1])}"

        return s  # fallback (se già formattato o formato diverso)

    def load_interventi(self):
        table = self.ui.tableInterventi
        rows = get_interventi_misti()  # sqlite3.Row

        table.setRowCount(len(rows))

        for r, row in enumerate(rows):
            tipo = row["tipo"]

            if tipo == "RICORRENTE":
                giorni = self.format_giorni(row["giorni"])
                data_fmt = "-"
                periodo_fmt = self.format_periodo(row["periodo"])
            else:
                giorni = "-"
                data_fmt = self.format_data(row["data"])
                periodo_fmt = "-"

            values = [
                row["id_ref"],
                row["tipo"],
                row["cliente"],
                row["servizio"],
                row["dipendenti"],
                data_fmt,
                row["ora"],
                self.format_durata_hhmm(row["durata"]),
                giorni,
                row["stato"],
                periodo_fmt,
            ]

            for c, v in enumerate(values):
                item = QTableWidgetItem("" if v is None else str(v))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                table.setItem(r, c, item)

        table.clearSelection()
        self.on_selection_changed()

    def aggiungi_intervento(self):
        scelta = QMessageBox.question(
            self.ui,
            "Aggiungi",
            "Vuoi aggiungere un intervento singolo?\n(Sì = Singolo, No = Ricorrente)",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if scelta == QMessageBox.StandardButton.No:
            # RICORRENTE (solo regola, nessuna istanza generata)
            dialog = RicorrenteDialog(parent=None)
            if dialog.exec() != dialog.DialogCode.Accepted:
                return

            dati = dialog.get_dati()

            try:
                create_ricorrente(dati)
                self.load_interventi()
            except Exception as e:
                import traceback
                traceback.print_exc()
                QMessageBox.critical(self.ui, "Errore", f"Errore durante il salvataggio del ricorrente:\n{e}")

            return

        # SINGOLO
        dialog = InterventoDialog(parent=None)
        if dialog.exec() != dialog.DialogCode.Accepted:
            return

        dati = dialog.get_dati()

        try:
            create_intervento(dati)
            self.load_interventi()
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self.ui, "Errore", f"Errore durante il salvataggio dell'intervento:\n{e}")

    def modifica_intervento(self):
        table = self.ui.tableInterventi
        row = table.currentRow()

        if row < 0:
            QMessageBox.warning(self.ui, "Modifica", "Seleziona prima una riga da modificare.")
            return

        id_ref = int(table.item(row, 0).text())  # ID_REF (nascosta)
        tipo = table.item(row, 1).text()  # TIPO (nascosta)

        # --- CASO 1: SINGOLO ---
        if tipo == "SINGOLO":
            intervento_id = id_ref

            it = get_intervento_by_id(intervento_id)
            if it is None:
                QMessageBox.warning(self.ui, "Errore", "Intervento non trovato.")
                return

            dip_ids = get_intervento_dipendenti_ids(intervento_id)

            dati_correnti = {
                "cliente_id": it["cliente_id"],
                "servizio_id": it["servizio_id"],
                "data": it["data"],
                "ora_inizio": it["ora_inizio"],
                "durata_ore": it["durata_ore"],
                "stato": it["stato"],
                "note": it["note"],
                "dipendente_ids": dip_ids
            }

            dialog = InterventoDialog(parent=None, intervento=dati_correnti)
            if dialog.exec() != dialog.DialogCode.Accepted:
                return

            nuovi_dati = dialog.get_dati()

            if not nuovi_dati["cliente_id"] or not nuovi_dati["servizio_id"]:
                QMessageBox.warning(self.ui, "Dati mancanti", "Cliente e servizio sono obbligatori.")
                return

            if not nuovi_dati["data"] or not nuovi_dati["ora_inizio"]:
                QMessageBox.warning(self.ui, "Dati mancanti", "Data e ora sono obbligatori.")
                return

            try:
                durata = float(str(nuovi_dati["durata_ore"]).replace(",", "."))
                if durata <= 0:
                    raise ValueError
                nuovi_dati["durata_ore"] = durata
            except:
                QMessageBox.warning(self.ui, "Dato non valido", "Durata ore deve essere un numero > 0.")
                return

            try:
                update_intervento(intervento_id, nuovi_dati)
                self.load_interventi()
            except Exception as e:
                import traceback
                traceback.print_exc()
                QMessageBox.critical(self.ui, "Errore", f"Errore durante la modifica dell'intervento:\n{e}")
            return


        # --- CASO 2: RICORRENTE ---
        elif tipo == "RICORRENTE":
            ricorrente_id = id_ref

            r = get_ricorrente_by_id(ricorrente_id)
            if r is None:
                QMessageBox.warning(self.ui, "Errore", "Ricorrente non trovato.")
                return

            dati_correnti = {
                "cliente_id": r["cliente_id"],
                "servizio_id": r["servizio_id"],
                "ora_inizio": r["ora_inizio"],
                "durata_ore": r["durata_ore"],
                "note": r["note"],
                "attivo": r["attivo"],
                "giorni_settimana": get_ricorrente_giorni(ricorrente_id),
                "dipendente_ids": get_ricorrente_dipendenti_ids(ricorrente_id),
            }

            dialog = RicorrenteDialog(parent=None, ricorrente=dati_correnti)
            if dialog.exec() != dialog.DialogCode.Accepted:
                return

            nuovi = dialog.get_dati()

            if not nuovi["cliente_id"] or not nuovi["servizio_id"]:
                QMessageBox.warning(self.ui, "Dati mancanti", "Cliente e servizio sono obbligatori.")
                return

            # ricorrente: serve ora_inizio
            if not nuovi.get("ora_inizio"):
                QMessageBox.warning(self.ui, "Dati mancanti", "Ora inizio è obbligatoria.")
                return

            # ricorrente: serve almeno 1 giorno
            if not nuovi.get("giorni_settimana"):
                QMessageBox.warning(self.ui, "Dati mancanti", "Seleziona almeno un giorno della settimana.")
                return

            try:
                durata = float(str(nuovi["durata_ore"]).replace(",", "."))
                if durata <= 0:
                    raise ValueError
                nuovi["durata_ore"] = durata
            except:
                QMessageBox.warning(self.ui, "Dato non valido", "Durata ore deve essere un numero > 0.")
                return

            try:
                update_ricorrente(ricorrente_id, nuovi)
                self.load_interventi()
            except Exception as e:
                import traceback
                traceback.print_exc()
                QMessageBox.critical(self.ui, "Errore", f"Errore durante la modifica del ricorrente:\n{e}")
            return

    def elimina_intervento(self):
        table = self.ui.tableInterventi
        row = table.currentRow()

        if row < 0:
            QMessageBox.warning(self.ui, "Elimina", "Seleziona prima una riga da eliminare.")
            return

        id_ref = int(table.item(row, 0).text())  # ID_REF (nascosta)
        tipo = table.item(row, 1).text()  # TIPO (nascosta)

        msg = "Sei sicuro di voler eliminare questo elemento?"
        if tipo == "RICORRENTE":
            msg = "Sei sicuro di voler eliminare questo ricorrente? (non eliminerà automaticamente gli interventi già generati)"

        risposta = QMessageBox.question(
            self.ui,
            "Conferma eliminazione",
            msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if risposta != QMessageBox.StandardButton.Yes:
            return

        try:
            if tipo == "SINGOLO":
                delete_intervento(id_ref)

            elif tipo == "RICORRENTE":
                delete_ricorrente(id_ref)  # ✅ qui

            else:
                QMessageBox.warning(self.ui, "Errore", f"Tipo non riconosciuto: {tipo}")
                return

            self.load_interventi()

        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self.ui, "Errore", f"Errore durante l'eliminazione:\n{e}")

    def on_selection_changed(self):
        ha_selezione = self.ui.tableInterventi.currentRow() >= 0
        self.ui.btnInterventiModifica.setEnabled(ha_selezione)
        self.ui.btnInterventiElimina.setEnabled(ha_selezione)
