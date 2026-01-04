from PyQt6.QtWidgets import QHeaderView, QAbstractItemView,QTableWidgetItem, QMessageBox

from database.database import get_connection
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
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

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

    def _norm(self, s: str) -> str:
        return " ".join(s.strip().split()).lower()

    # ---------------------------------------------------------
    #  AGGIUNGI DIPENDENTE
    # ---------------------------------------------------------
    def aggiungi_dipendente(self):
        dialog = DipendenteDialog(parent=None)
        if dialog.exec() != dialog.DialogCode.Accepted:
            return

        dati = dialog.get_dati()

        # normalizzo nome/cognome (tolgo doppi spazi)
        dati["nome"] = " ".join(dati["nome"].strip().split())
        dati["cognome"] = " ".join(dati["cognome"].strip().split())

        # obbligatori
        if not dati["nome"] or not dati["cognome"]:
            QMessageBox.warning(self.ui, "Dati mancanti", "Nome e cognome sono obbligatori.")
            return

        if not dati["stipendio"]:
            QMessageBox.warning(self.ui, "Dati mancanti", "Lo stipendio è obbligatorio.")
            return

        if not dati["scadenza_contratto"]:
            QMessageBox.warning(self.ui, "Dati mancanti", "La scadenza del contratto è obbligatoria.")
            return

        # stipendio: numero > 0
        try:
            stipendio = float(str(dati["stipendio"]).replace(",", "."))
            if stipendio <= 0:
                raise ValueError
            dati["stipendio"] = stipendio
        except ValueError:
            QMessageBox.warning(self.ui, "Dato non valido", "Inserisci uno stipendio valido (> 0).")
            return

        # ore settimanali: se inserite devono essere int > 0
        if dati.get("ore_settimanali"):
            try:
                ore = int(str(dati["ore_settimanali"]).strip())
                if ore <= 0:
                    raise ValueError
                dati["ore_settimanali"] = ore
            except ValueError:
                QMessageBox.warning(self.ui, "Dato non valido", "Ore settimanali deve essere un intero > 0.")
                return
        else:
            dati["ore_settimanali"] = None

        # duplicati (robusto)
        conn = get_connection()
        cur = conn.cursor()
        nome_n = self._norm(dati["nome"])
        cognome_n = self._norm(dati["cognome"])
        cur.execute(
            "SELECT 1 FROM dipendenti WHERE lower(trim(nome)) = ? AND lower(trim(cognome)) = ? LIMIT 1",
            (nome_n, cognome_n)
        )
        if cur.fetchone():
            QMessageBox.warning(self.ui, "Dipendente esistente",
                                "Esiste già un dipendente con lo stesso nome e cognome.")
            return

        try:
            Dipendente.create(dati)
            self.load_dipendenti()
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self.ui, "Errore", f"Errore durante il salvataggio del dipendente:\n{e}")

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

        # normalizzo
        nuovi_dati["nome"] = " ".join(nuovi_dati["nome"].strip().split())
        nuovi_dati["cognome"] = " ".join(nuovi_dati["cognome"].strip().split())

        # obbligatori
        if not nuovi_dati["nome"] or not nuovi_dati["cognome"]:
            QMessageBox.warning(self.ui, "Dati mancanti", "Nome e cognome sono obbligatori.")
            return

        if not nuovi_dati["stipendio"]:
            QMessageBox.warning(self.ui, "Dati mancanti", "Lo stipendio è obbligatorio.")
            return

        if not nuovi_dati["scadenza_contratto"]:
            QMessageBox.warning(self.ui, "Dati mancanti", "La scadenza del contratto è obbligatoria.")
            return

        # stipendio: numero > 0
        try:
            stipendio = float(str(nuovi_dati["stipendio"]).replace(",", "."))
            if stipendio <= 0:
                raise ValueError
            nuovi_dati["stipendio"] = stipendio
        except ValueError:
            QMessageBox.warning(self.ui, "Dato non valido", "Inserisci uno stipendio valido (> 0).")
            return

        # ore settimanali: se inserite devono essere int > 0
        if nuovi_dati.get("ore_settimanali"):
            try:
                ore = int(str(nuovi_dati["ore_settimanali"]).strip())
                if ore <= 0:
                    raise ValueError
                nuovi_dati["ore_settimanali"] = ore
            except ValueError:
                QMessageBox.warning(self.ui, "Dato non valido", "Ore settimanali deve essere un intero > 0.")
                return
        else:
            nuovi_dati["ore_settimanali"] = None

        # duplicati (escludo me stesso)
        conn = get_connection()
        cur = conn.cursor()
        nome_n = self._norm(nuovi_dati["nome"])
        cognome_n = self._norm(nuovi_dati["cognome"])
        cur.execute(
            "SELECT 1 FROM dipendenti WHERE lower(trim(nome)) = ? AND lower(trim(cognome)) = ? AND id != ? LIMIT 1",
            (nome_n, cognome_n, dipendente_id)
        )
        if cur.fetchone():
            QMessageBox.warning(self.ui, "Dipendente esistente",
                                "Esiste già un dipendente con lo stesso nome e cognome.")
            return

        try:
            Dipendente.update(dipendente_id, nuovi_dati)
            self.load_dipendenti()

            if hasattr(self.ui, "interventi_section"):
                self.ui.interventi_section.load_interventi()
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

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT 1 FROM interventi_dipendenti WHERE dipendente_id = ? LIMIT 1", (dipendente_id,))
        if cur.fetchone():
            QMessageBox.warning(self.ui, "Impossibile eliminare",
                                "Non puoi eliminare il dipendente perché è assegnato ad almeno un intervento.")
            return

        cur.execute("SELECT 1 FROM ricorrenti_dipendenti WHERE dipendente_id = ? LIMIT 1", (dipendente_id,))
        if cur.fetchone():
            QMessageBox.warning(self.ui, "Impossibile eliminare",
                                "Non puoi eliminare il dipendente perché è assegnato ad almeno un intervento ricorrente.")
            return

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
