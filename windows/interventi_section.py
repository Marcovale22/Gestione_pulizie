from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHeaderView, QAbstractItemView, QTableWidgetItem, QMessageBox

from models.intervento import Intervento
from dialogs.intervento_dialog import InterventoDialog
from database.repositories.interventi_repo import (
    get_interventi_misti,
    get_intervento_by_id,
    get_intervento_dipendenti_ids,
    create_intervento,
    update_intervento,
    delete_intervento
)



class InterventiSection:
    def __init__(self, ui):
        self.ui = ui
        self.setup_table()
        self.setup_signals()
        self.load_interventi()

        self.ui.btnInterventiModifica.setEnabled(False)
        self.ui.btnInterventiElimina.setEnabled(False)

    def setup_table(self):
        table = self.ui.tableInterventi

        table.setColumnCount(10)
        table.setHorizontalHeaderLabels([
            "ID_REF", "TIPO", "Cliente", "Servizio", "Dipendenti",
            "Data", "Ora", "Durata", "Giorni", "Stato"
        ])

        table.setColumnHidden(0, True)  # ID_REF
        table.setColumnHidden(1, True)  # TIPO

        header = table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

        table.setAlternatingRowColors(True)
        table.verticalHeader().setVisible(False)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        table.setShowGrid(True)
        table.setWordWrap(False)

        table.setStyleSheet(self.ui.tableClienti.styleSheet())

        table.setColumnWidth(2, 200)  # Cliente
        table.setColumnWidth(3, 160)  # Servizio
        table.setColumnWidth(4, 220)  # Dipendenti

    def setup_signals(self):
        self.ui.btnInterventiAggiungi.clicked.connect(self.aggiungi_intervento)
        self.ui.btnInterventiModifica.clicked.connect(self.modifica_intervento)
        self.ui.btnInterventiElimina.clicked.connect(self.elimina_intervento)

        self.ui.tableInterventi.itemSelectionChanged.connect(self.on_selection_changed)

    def format_giorni(csv_nums: str) -> str:
        if not csv_nums or str(csv_nums).strip() in ("-", ""):
            return "-"
        MAP = {1: "Lun", 2: "Mar", 3: "Mer", 4: "Gio", 5: "Ven", 6: "Sab", 7: "Dom"}
        parts = [p.strip() for p in str(csv_nums).split(",")]
        nums = sorted({int(p) for p in parts if p.isdigit() and int(p) in MAP})
        return ", ".join(MAP[n] for n in nums) if nums else "-"

    def load_interventi(self):
        table = self.ui.tableInterventi
        rows = get_interventi_misti()  # sqlite3.Row

        table.setRowCount(len(rows))

        for r, row in enumerate(rows):
            tipo = row["tipo"]
            giorni = row["giorni"]
            if tipo == "RICORRENTE":
                giorni = self.format_giorni(giorni)
            else:
                giorni = "-"

            values = [
                row["id_ref"],  # 0 hidden
                row["tipo"],  # 1 hidden
                row["cliente"],  # 2
                row["servizio"],  # 3
                row["dipendenti"],  # 4
                row["data"],  # 5
                row["ora"],  # 6
                row["durata"],  # 7
                giorni,  # 8
                row["stato"],  # 9
            ]

            for c, v in enumerate(values):
                item = QTableWidgetItem("" if v is None else str(v))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                table.setItem(r, c, item)

        table.clearSelection()
        self.on_selection_changed()

    def aggiungi_intervento(self):
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

        # --- CASO 1: INTERVENTO SINGOLO (istanza reale) ---
        if tipo == "SINGOLO":
            intervento_id = id_ref

            # meglio: recupero by id (se non lo hai ancora, va bene anche all())
            it = get_intervento_by_id(intervento_id)
            if it is None:
                QMessageBox.warning(self.ui, "Errore", "Intervento non trovato.")
                return

            dip_ids = get_intervento_dipendenti_ids(intervento_id)

            if it is None:
                QMessageBox.warning(self.ui, "Errore", "Intervento non trovato.")
                return

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
            QMessageBox.information(
                self.ui,
                "Modifica ricorrente",
                f"Qui apriremo il dialog del ricorrente (ID={ricorrente_id})."
            )
            return

        else:
            QMessageBox.warning(self.ui, "Errore", f"Tipo non riconosciuto: {tipo}")
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
                delete_intervento(id_ref)  # ✅ qui usi id_ref

            elif tipo == "RICORRENTE":
                QMessageBox.information(
                    self.ui,
                    "Elimina ricorrente",
                    f"Qui elimineremo il ricorrente (ID={id_ref})."
                )
                return

            else:
                QMessageBox.warning(self.ui, "Errore", f"Tipo non riconosciuto: {tipo}")
                return

            self.load_interventi()  # ✅ una sola volta

        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self.ui, "Errore", f"Errore durante l'eliminazione:\n{e}")

    def on_selection_changed(self):
        ha_selezione = self.ui.tableInterventi.currentRow() >= 0
        self.ui.btnInterventiModifica.setEnabled(ha_selezione)
        self.ui.btnInterventiElimina.setEnabled(ha_selezione)
