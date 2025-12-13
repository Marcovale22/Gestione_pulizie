from PyQt6.QtWidgets import QHeaderView, QAbstractItemView, QTableWidgetItem, QMessageBox
from models.servizi import Servizio
from dialogs.servizio_dialog import ServizioDialog


class ServiziSection:
    def __init__(self, ui):
        self.ui = ui
        self.setup_table()
        self.setup_signals()
        self.load_servizi()

    def setup_table(self):
        table = self.ui.tableServizi

        table.setColumnCount(4)
        table.setHorizontalHeaderLabels([
            "ID", "Nome", "Descrizione", "Prezzo orario (€)"
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

        # stesso stile della tabella clienti
        table.setStyleSheet(self.ui.tableClienti.styleSheet())

        # un po' più larga la descrizione
        table.setColumnWidth(2, 320)

    def setup_signals(self):
        self.ui.btnServiziAggiungi.clicked.connect(self.aggiungi_servizio)
        self.ui.btnServiziModifica.clicked.connect(self.modifica_servizio)
        self.ui.btnServiziElimina.clicked.connect(self.elimina_servizio)

        self.ui.tableServizi.itemSelectionChanged.connect(self.on_selection_changed)

    def load_servizi(self):
        table = self.ui.tableServizi
        servizi = Servizio.all()

        table.setRowCount(len(servizi))

        for row_idx, s in enumerate(servizi):
            table.setItem(row_idx, 0, QTableWidgetItem(str(s.id)))
            table.setItem(row_idx, 1, QTableWidgetItem(s.nome))
            table.setItem(row_idx, 2, QTableWidgetItem(s.descrizione or ""))
            table.setItem(row_idx, 3, QTableWidgetItem("" if s.prezzo_orario is None else f"{s.prezzo_orario:.2f}"))

        table.clearSelection()
        self.on_selection_changed()

    def aggiungi_servizio(self):
        dialog = ServizioDialog(parent=None)
        if dialog.exec() != dialog.DialogCode.Accepted:
            return

        dati = dialog.get_dati()

        try:
            Servizio.create(dati)
            self.load_servizi()
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self.ui, "Errore", f"Errore durante il salvataggio del servizio:\n{e}")

    def modifica_servizio(self):
        table = self.ui.tableServizi
        row = table.currentRow()

        if row < 0:
            QMessageBox.warning(self.ui, "Modifica servizio", "Seleziona prima un servizio da modificare.")
            return

        servizio_id = int(table.item(row, 0).text())
        dati_correnti = {
            "nome": table.item(row, 1).text(),
            "descrizione": table.item(row, 2).text(),
            "prezzo_orario": table.item(row, 3).text().replace(",", "."),
        }

        dialog = ServizioDialog(parent=None, servizio=dati_correnti)
        if dialog.exec() != dialog.DialogCode.Accepted:
            return

        nuovi_dati = dialog.get_dati()

        try:
            Servizio.update(servizio_id, nuovi_dati)
            self.load_servizi()
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self.ui, "Errore", f"Errore durante la modifica del servizio:\n{e}")

    def elimina_servizio(self):
        table = self.ui.tableServizi
        row = table.currentRow()

        if row < 0:
            QMessageBox.warning(self.ui, "Elimina servizio", "Seleziona prima un servizio da eliminare.")
            return

        servizio_id = int(table.item(row, 0).text())

        risposta = QMessageBox.question(
            self.ui,
            "Conferma eliminazione",
            "Sei sicuro di voler eliminare questo servizio?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if risposta != QMessageBox.StandardButton.Yes:
            return

        try:
            Servizio.delete(servizio_id)
            self.load_servizi()
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self.ui, "Errore", f"Errore durante l'eliminazione del servizio:\n{e}")

    def on_selection_changed(self):
        ha_selezione = self.ui.tableServizi.currentRow() >= 0
        self.ui.btnServiziModifica.setEnabled(ha_selezione)
        self.ui.btnServiziElimina.setEnabled(ha_selezione)
