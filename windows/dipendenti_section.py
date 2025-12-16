from PyQt6.QtWidgets import QHeaderView, QAbstractItemView,QTableWidgetItem, QMessageBox
from models.dipendenti import Dipendente
from dialogs.dipendente_dialog import DipendenteDialog
from datetime import datetime, date

class DipendentiSection:
    def __init__(self, ui):
        self.ui = ui
        self.setup_table()
        self.setup_signals()
        self.load_dipendenti()

    def setup_table(self):
        table = self.ui.tableDipendenti

        table.setColumnCount(9)
        table.setHorizontalHeaderLabels([
            "ID", "Nome", "Cognome", "Telefono", "Email",
            "Mansione", "Ore sett.", "Stipendio (€)", "Scadenza contratto"
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

        # stesso stile grafico della tabella clienti
        table.setStyleSheet(self.ui.tableClienti.styleSheet())

        # 👇 FIX header lungo
        table.setColumnWidth(8, 160)
    def setup_signals(self):
        self.ui.btnDipendentiAggiungi.clicked.connect(self.aggiungi_dipendente)
        self.ui.btnDipendentiModifica.clicked.connect(self.modifica_dipendente)
        self.ui.btnDipendentiElimina.clicked.connect(self.elimina_dipendente)

        self.ui.tableDipendenti.itemSelectionChanged.connect(self.on_selection_changed)

    def format_data(self, value) -> str:
        if value is None:
            return ""

        if isinstance(value, (date, datetime)):
            return value.strftime("%d-%m-%Y")

        s = str(value).strip()
        if not s or s == "-":
            return ""

        # se arriva "YYYY-MM-DD HH:MM:SS" prendo solo la parte data
        s = s[:10]

        try:
            return datetime.strptime(s, "%Y-%m-%d").strftime("%d-%m-%Y")
        except ValueError:
            return str(value)  # fallback

    # ---------------------------------------------------------
    #  LOAD DIPENDENTI
    # ---------------------------------------------------------
    def load_dipendenti(self):
        table = self.ui.tableDipendenti
        dipendenti = Dipendente.all()   # come Cliente.all()

        table.setRowCount(len(dipendenti))

        for row_idx, d in enumerate(dipendenti):
            # colonna ID nascosta
            table.setItem(row_idx, 0, QTableWidgetItem(str(d.id)))

            # colonne visibili
            table.setItem(row_idx, 1, QTableWidgetItem(d.nome))
            table.setItem(row_idx, 2, QTableWidgetItem(d.cognome))
            table.setItem(row_idx, 3, QTableWidgetItem(d.telefono or ""))
            table.setItem(row_idx, 4, QTableWidgetItem(d.email or ""))
            table.setItem(row_idx, 5, QTableWidgetItem(d.mansione or ""))
            table.setItem(row_idx, 6, QTableWidgetItem(str(d.ore_settimanali) if d.ore_settimanali is not None else ""))
            table.setItem(row_idx, 7, QTableWidgetItem(str(d.stipendio) if d.stipendio is not None else ""))
            table.setItem(row_idx, 8, QTableWidgetItem(self.format_data(d.scadenza_contratto)))


        table.clearSelection()
        self.on_selection_changed()

    # ---------------------------------------------------------
    #  AGGIUNGI DIPENDENTE
    # ---------------------------------------------------------
    def aggiungi_dipendente(self):
        dialog = DipendenteDialog(parent=None)
        if dialog.exec() != dialog.DialogCode.Accepted:
            return

        dati = dialog.get_dati()

        try:
            Dipendente.create(dati)
            self.load_dipendenti()
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(
                self.ui,  # o None se preferisci
                "Errore",
                f"Errore durante il salvataggio del dipendente:\n{e}"
            )
    # ---------------------------------------------------------
    #  MODIFICA DIPENDENTE
    # ---------------------------------------------------------
    def modifica_dipendente(self):
        table = self.ui.tableDipendenti
        row = table.currentRow()

        if row < 0:
            QMessageBox.warning(
                self.ui,
                "Modifica dipendente",
                "Seleziona prima un dipendente da modificare."
            )
            return

        dipendente_id = int(table.item(row, 0).text())

        dati_correnti = {
            "nome": table.item(row, 1).text(),
            "cognome": table.item(row, 2).text(),
            "telefono": table.item(row, 3).text(),
            "email": table.item(row, 4).text(),
            "mansione": table.item(row, 5).text(),
            "ore_settimanali": table.item(row, 6).text(),
            "stipendio": table.item(row, 7).text(),
            "scadenza_contratto": table.item(row, 8).text(),
        }

        dialog = DipendenteDialog(parent=None, dipendente=dati_correnti)
        if dialog.exec() != dialog.DialogCode.Accepted:
            return  # l'utente ha annullato

        nuovi_dati = dialog.get_dati()

        try:
            Dipendente.update(dipendente_id, nuovi_dati)
            self.load_dipendenti()
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(
                self.ui,
                "Errore",
                f"Errore durante la modifica del dipendente:\n{e}"
            )

    # ---------------------------------------------------------
    #  ELIMINA DIPENDENTE
    # ---------------------------------------------------------
    def elimina_dipendente(self):
        table = self.ui.tableDipendenti
        row = table.currentRow()

        if row < 0:
            QMessageBox.warning(
                self.ui,
                "Elimina dipendente",
                "Seleziona prima un dipendente da eliminare."
            )
            return

        dipendente_id = int(table.item(row, 0).text())

        risposta = QMessageBox.question(
            self.ui,
            "Conferma eliminazione",
            "Sei sicuro di voler eliminare questo dipendente?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if risposta != QMessageBox.StandardButton.Yes:
            return

        try:
            Dipendente.delete(dipendente_id)
            self.load_dipendenti()
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(
                self.ui,
                "Errore",
                f"Errore durante l'eliminazione del dipendente:\n{e}"
            )

    # ---------------------------------------------------------
    #  GESTIONE SELEZIONE
    # ---------------------------------------------------------
    def on_selection_changed(self):
        ha_selezione = self.ui.tableDipendenti.currentRow() >= 0
        self.ui.btnDipendentiModifica.setEnabled(ha_selezione)
        self.ui.btnDipendentiElimina.setEnabled(ha_selezione)
