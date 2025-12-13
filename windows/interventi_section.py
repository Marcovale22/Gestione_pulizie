from PyQt6.QtWidgets import QHeaderView, QAbstractItemView, QTableWidgetItem, QMessageBox

from models.intervento import Intervento
from models.cliente import Cliente
from models.dipendenti import Dipendente
from models.servizi import Servizio
from dialogs.intervento_dialog import InterventoDialog


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

        table.setColumnCount(8)
        table.setHorizontalHeaderLabels([
            "ID", "Cliente", "Servizio", "Dipendente",
            "Data", "Ora", "Durata", "Stato"
        ])
        table.setColumnHidden(0, True)

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

        table.setColumnWidth(1, 200)  # Cliente
        table.setColumnWidth(2, 160)  # Servizio
        table.setColumnWidth(3, 180)  # Dipendente

    def setup_signals(self):
        self.ui.btnInterventiAggiungi.clicked.connect(self.aggiungi_intervento)
        self.ui.btnInterventiModifica.clicked.connect(self.modifica_intervento)
        self.ui.btnInterventiElimina.clicked.connect(self.elimina_intervento)

        self.ui.tableInterventi.itemSelectionChanged.connect(self.on_selection_changed)

    def load_interventi(self):
        table = self.ui.tableInterventi
        interventi = Intervento.all()

        # mappe id -> nome visuale
        clienti_map = {c.id: f"{c.cognome} {c.nome}" for c in Cliente.all()}
        servizi_map = {s.id: s.nome for s in Servizio.all()}
        dip_map = {d.id: f"{d.cognome} {d.nome}" for d in Dipendente.all()}

        table.setRowCount(len(interventi))

        for row_idx, it in enumerate(interventi):
            table.setItem(row_idx, 0, QTableWidgetItem(str(it.id)))
            table.setItem(row_idx, 1, QTableWidgetItem(clienti_map.get(it.cliente_id, f"ID {it.cliente_id}")))
            table.setItem(row_idx, 2, QTableWidgetItem(servizi_map.get(it.servizio_id, f"ID {it.servizio_id}")))

            dip_txt = "Non assegnato" if it.dipendente_id is None else dip_map.get(it.dipendente_id, f"ID {it.dipendente_id}")
            table.setItem(row_idx, 3, QTableWidgetItem(dip_txt))

            table.setItem(row_idx, 4, QTableWidgetItem(it.data))
            table.setItem(row_idx, 5, QTableWidgetItem(it.ora_inizio))
            table.setItem(row_idx, 6, QTableWidgetItem("" if it.durata_ore is None else str(it.durata_ore)))
            table.setItem(row_idx, 7, QTableWidgetItem(it.stato))

        table.clearSelection()
        self.on_selection_changed()

    def aggiungi_intervento(self):
        dialog = InterventoDialog(parent=None)
        if dialog.exec() != dialog.DialogCode.Accepted:
            return

        dati = dialog.get_dati()

        try:
            Intervento.create(dati)
            self.load_interventi()
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self.ui, "Errore", f"Errore durante il salvataggio dell'intervento:\n{e}")

    def modifica_intervento(self):
        table = self.ui.tableInterventi
        row = table.currentRow()

        if row < 0:
            QMessageBox.warning(self.ui, "Modifica intervento", "Seleziona prima un intervento da modificare.")
            return

        intervento_id = int(table.item(row, 0).text())

        # qui dobbiamo recuperare i valori originali dal DB (più sicuro)
        # per semplicità: prendiamo tutto da Intervento.all e cerchiamo l'id
        it = next((x for x in Intervento.all() if x.id == intervento_id), None)
        if it is None:
            QMessageBox.warning(self.ui, "Errore", "Intervento non trovato.")
            return

        dati_correnti = {
            "cliente_id": it.cliente_id,
            "servizio_id": it.servizio_id,
            "dipendente_id": it.dipendente_id,
            "data": it.data,
            "ora_inizio": it.ora_inizio,
            "durata_ore": it.durata_ore,
            "stato": it.stato,
            "note": it.note,
        }

        dialog = InterventoDialog(parent=None, intervento=dati_correnti)
        if dialog.exec() != dialog.DialogCode.Accepted:
            return

        nuovi_dati = dialog.get_dati()

        try:
            Intervento.update(intervento_id, nuovi_dati)
            self.load_interventi()
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self.ui, "Errore", f"Errore durante la modifica dell'intervento:\n{e}")

    def elimina_intervento(self):
        table = self.ui.tableInterventi
        row = table.currentRow()

        if row < 0:
            QMessageBox.warning(self.ui, "Elimina intervento", "Seleziona prima un intervento da eliminare.")
            return

        intervento_id = int(table.item(row, 0).text())

        risposta = QMessageBox.question(
            self.ui,
            "Conferma eliminazione",
            "Sei sicuro di voler eliminare questo intervento?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if risposta != QMessageBox.StandardButton.Yes:
            return

        try:
            Intervento.delete(intervento_id)
            self.load_interventi()
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self.ui, "Errore", f"Errore durante l'eliminazione dell'intervento:\n{e}")

    def on_selection_changed(self):
        ha_selezione = self.ui.tableInterventi.currentRow() >= 0
        self.ui.btnInterventiModifica.setEnabled(ha_selezione)
        self.ui.btnInterventiElimina.setEnabled(ha_selezione)
