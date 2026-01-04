from PyQt6.QtWidgets import QHeaderView, QAbstractItemView, QTableWidgetItem, QMessageBox

from database.database import get_connection
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
            "ID", "Nome", "Descrizione", "Prezzo mensile (€)"
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
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

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
            table.setItem(row_idx, 3, QTableWidgetItem("" if s.prezzo_mensile is None else f"{s.prezzo_mensile:.2f}"))

        table.clearSelection()
        self.on_selection_changed()

    def _norm(self, s: str) -> str:
        return " ".join(s.strip().split()).lower()

    def aggiungi_servizio(self):
        dialog = ServizioDialog(parent=None)
        if dialog.exec() != dialog.DialogCode.Accepted:
            return

        dati = dialog.get_dati()

        # normalizzo nome (tolgo doppi spazi)
        dati["nome"] = " ".join(dati["nome"].strip().split())

        # 1) obbligatorio
        if not dati["nome"]:
            QMessageBox.warning(self.ui, "Dati mancanti", "Il nome del servizio è obbligatorio.")
            return

        # 2) prezzo mensile obbligatorio e valido
        if not dati.get("prezzo_mensile"):
            QMessageBox.warning(self.ui, "Dati mancanti", "Il prezzo mensile è obbligatorio.")
            return

        try:
            prezzo = float(str(dati["prezzo_mensile"]).replace(",", "."))
            if prezzo <= 0:
                raise ValueError
            dati["prezzo_mensile"] = prezzo
        except ValueError:
            QMessageBox.warning(self.ui, "Dato non valido", "Inserisci un prezzo mensile valido (> 0).")
            return

        # 3) duplicati (robusto)
        conn = get_connection()
        cur = conn.cursor()
        nome_n = self._norm(dati["nome"])

        cur.execute(
            "SELECT 1 FROM servizi WHERE lower(trim(nome)) = ? LIMIT 1",
            (nome_n,)
        )
        if cur.fetchone():
            QMessageBox.warning(self.ui, "Servizio esistente", "Esiste già un servizio con lo stesso nome.")
            return

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
            "prezzo_mensile": table.item(row, 3).text().replace(",", "."),
        }

        dialog = ServizioDialog(parent=None, servizio=dati_correnti)
        if dialog.exec() != dialog.DialogCode.Accepted:
            return

        nuovi_dati = dialog.get_dati()

        nuovi_dati["nome"] = " ".join(nuovi_dati["nome"].strip().split())

        # 1) obbligatorio
        if not nuovi_dati["nome"]:
            QMessageBox.warning(self.ui, "Dati mancanti", "Il nome del servizio è obbligatorio.")
            return

        # 2) prezzo valido
        if not nuovi_dati.get("prezzo_mensile"):
            QMessageBox.warning(self.ui, "Dati mancanti", "Il prezzo mensile è obbligatorio.")
            return

        try:
            prezzo = float(str(nuovi_dati["prezzo_mensile"]).replace(",", "."))
            if prezzo <= 0:
                raise ValueError
            nuovi_dati["prezzo_mensile"] = prezzo
        except ValueError:
            QMessageBox.warning(self.ui, "Dato non valido", "Inserisci un prezzo mensile valido (> 0).")
            return

        # 3) duplicati (escludo me stesso)
        conn = get_connection()
        cur = conn.cursor()
        nome_n = self._norm(nuovi_dati["nome"])

        cur.execute(
            "SELECT 1 FROM servizi WHERE lower(trim(nome)) = ? AND id != ? LIMIT 1",
            (nome_n, servizio_id)
        )
        if cur.fetchone():
            QMessageBox.warning(self.ui, "Servizio esistente", "Esiste già un servizio con lo stesso nome.")
            return

        try:
            Servizio.update(servizio_id, nuovi_dati)
            self.load_servizi()
            if hasattr(self.ui, "interventi_section"):
                self.ui.interventi_section.load_interventi()

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

        conn = get_connection()
        cur = conn.cursor()

        # blocco se associato a interventi
        cur.execute("SELECT 1 FROM interventi WHERE servizio_id = ? LIMIT 1", (servizio_id,))
        if cur.fetchone():
            QMessageBox.warning(self.ui, "Impossibile eliminare",
                                "Non puoi eliminare il servizio perché è associato ad almeno un intervento.")
            return

        # blocco se associato a ricorrenti
        cur.execute("SELECT 1 FROM interventi_ricorrenti WHERE servizio_id = ? LIMIT 1", (servizio_id,))
        if cur.fetchone():
            QMessageBox.warning(self.ui, "Impossibile eliminare",
                                "Non puoi eliminare il servizio perché è associato ad almeno un intervento ricorrente.")
            return

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
