from PyQt6.QtWidgets import (
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
    QAbstractItemView
)


from models.cliente import Cliente
from database.database import get_connection
from dialogs.cliente_dialog import ClienteDialog


class ClientiSection:
    def __init__(self, ui):
        self.ui = ui

        self.setup_table()
        self.setup_signals()
        self.load_clienti()

        # Pulsanti disabilitati all'avvio
        self.ui.btnClienteModifica.setEnabled(False)
        self.ui.btnClienteElimina.setEnabled(False)

    # ---------------------------------------------------------
    #  SETUP TABELLA
    # ---------------------------------------------------------
    def setup_table(self):
        table = self.ui.tableClienti


        # 6 colonne: ID nascosto + 5 campi visibili
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels([
            "ID", "Nome", "Cognome", "Telefono", "Indirizzo", "Email"
        ])

        # Nascondo colonna ID
        table.setColumnHidden(0, True)

        header = table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

        table.setAlternatingRowColors(True)
        table.verticalHeader().setVisible(False)
        table.setShowGrid(True)
        table.setWordWrap(False)
        table.setHorizontalScrollMode(table.ScrollMode.ScrollPerPixel)
        table.setVerticalScrollMode(table.ScrollMode.ScrollPerPixel)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

    # ---------------------------------------------------------
    #  SIGNALS
    # ---------------------------------------------------------
    def setup_signals(self):
        table = self.ui.tableClienti

        # quando cambia la selezione nella tabella
        table.itemSelectionChanged.connect(self.on_selection_changed)

        # click sui pulsanti
        self.ui.btnClienteAggiungi.clicked.connect(self.aggiungi_cliente)
        self.ui.btnClienteModifica.clicked.connect(self.modifica_cliente)
        self.ui.btnClienteElimina.clicked.connect(self.elimina_cliente)

    # ---------------------------------------------------------
    #  CARICAMENTO DATI
    # ---------------------------------------------------------
    def load_clienti(self):
        table = self.ui.tableClienti
        clienti = Cliente.all()      # prende i clienti dal model

        table.setRowCount(len(clienti))

        for row_idx, cliente in enumerate(clienti):
            # Colonna ID nascosta
            table.setItem(row_idx, 0, QTableWidgetItem(str(cliente.id)))

            # Colonne visibili
            table.setItem(row_idx, 1, QTableWidgetItem(cliente.nome))
            table.setItem(row_idx, 2, QTableWidgetItem(cliente.cognome))
            table.setItem(row_idx, 3, QTableWidgetItem(cliente.telefono or ""))
            table.setItem(row_idx, 4, QTableWidgetItem(cliente.indirizzo or ""))
            table.setItem(row_idx, 5, QTableWidgetItem(cliente.email or ""))

        # dopo il reload tolgo la selezione e aggiorno i pulsanti
        table.clearSelection()
        self.on_selection_changed()

    # ---------------------------------------------------------
    #  AGGIUNGI CLIENTE
    # ---------------------------------------------------------

    def _norm(self, s: str) -> str:
        # toglie spazi extra e rende case-insensitive (più robusto di lower)
        return " ".join(s.strip().split()).casefold()

    def aggiungi_cliente(self):
        dialog = ClienteDialog(parent=None)
        result = dialog.exec()

        if result != dialog.DialogCode.Accepted:
            return

        dati = dialog.get_dati()

        # --- Normalizzo ---
        dati["nome"] = " ".join(dati["nome"].strip().split())
        dati["cognome"] = " ".join(dati["cognome"].strip().split())

        # --- 1) CONTROLLI OBBLIGATORI ---
        if not dati["nome"] or not dati["cognome"]:
            QMessageBox.warning(self.ui, "Dati mancanti", "Nome e cognome sono obbligatori.")
            return

        conn = get_connection()
        cur = conn.cursor()

        # --- 2) CONTROLLO DUPLICATI (robusto) ---
        nome_n = self._norm(dati["nome"])
        cognome_n = self._norm(dati["cognome"])

        cur.execute(
            "SELECT 1 FROM clienti WHERE lower(trim(nome)) = ? AND lower(trim(cognome)) = ?",
            (nome_n, cognome_n)
        )
        if cur.fetchone():
            QMessageBox.warning(self.ui, "Cliente esistente", "Esiste già un cliente con lo stesso nome e cognome.")
            return

        # --- 3) INSERT ---
        cur.execute("""
            INSERT INTO clienti (nome, cognome, telefono, indirizzo, email)
            VALUES (?, ?, ?, ?, ?)
        """, (
            dati["nome"],
            dati["cognome"],
            dati["telefono"],
            dati["indirizzo"],
            dati["email"],
        ))
        conn.commit()
        self.load_clienti()

    def modifica_cliente(self):
        table = self.ui.tableClienti
        row = table.currentRow()

        if row < 0:
            QMessageBox.warning(self.ui, "Modifica cliente", "Seleziona prima un cliente da modificare.")
            return

        cliente_id = int(table.item(row, 0).text())

        dati_correnti = {
            "nome": table.item(row, 1).text(),
            "cognome": table.item(row, 2).text(),
            "telefono": table.item(row, 3).text(),
            "indirizzo": table.item(row, 4).text(),
            "email": table.item(row, 5).text(),
        }

        dialog = ClienteDialog(parent=None, cliente=dati_correnti)
        result = dialog.exec()

        if result != dialog.DialogCode.Accepted:
            return

        nuovi_dati = dialog.get_dati()

        # --- Normalizzo ---
        nuovi_dati["nome"] = " ".join(nuovi_dati["nome"].strip().split())
        nuovi_dati["cognome"] = " ".join(nuovi_dati["cognome"].strip().split())

        # --- 1) obbligatori ---
        if not nuovi_dati["nome"] or not nuovi_dati["cognome"]:
            QMessageBox.warning(self.ui, "Dati mancanti", "Nome e cognome sono obbligatori.")
            return

        conn = get_connection()
        cur = conn.cursor()

        # --- 2) duplicati (robusto + escludo me stesso) ---
        nome_n = self._norm(nuovi_dati["nome"])
        cognome_n = self._norm(nuovi_dati["cognome"])

        cur.execute(
            "SELECT 1 FROM clienti WHERE lower(trim(nome)) = ? AND lower(trim(cognome)) = ? AND id != ?",
            (nome_n, cognome_n, cliente_id)
        )
        if cur.fetchone():
            QMessageBox.warning(self.ui, "Cliente esistente", "Esiste già un cliente con lo stesso nome e cognome.")
            return

        # --- 3) update ---
        cur.execute("""
            UPDATE clienti
            SET nome = ?, cognome = ?, telefono = ?, indirizzo = ?, email = ?
            WHERE id = ?
        """, (
            nuovi_dati["nome"],
            nuovi_dati["cognome"],
            nuovi_dati["telefono"],
            nuovi_dati["indirizzo"],
            nuovi_dati["email"],
            cliente_id
        ))
        conn.commit()
        self.load_clienti()
        if hasattr(self.ui, "interventi_section"):
            self.ui.interventi_section.load_interventi()

    # ---------------------------------------------------------
    #  ELIMINA CLIENTE
    # ---------------------------------------------------------
    def elimina_cliente(self):
        table = self.ui.tableClienti
        row = table.currentRow()

        if row < 0:
            QMessageBox.warning(self.ui, "Elimina cliente", "Seleziona prima un cliente da eliminare.")
            return

        cliente_id = int(table.item(row, 0).text())

        conn = get_connection()
        cur = conn.cursor()

        # blocco se associato
        cur.execute("SELECT 1 FROM interventi WHERE cliente_id = ? LIMIT 1", (cliente_id,))
        if cur.fetchone():
            QMessageBox.warning(self.ui, "Impossibile eliminare",
                                "Non puoi eliminare il cliente perché è associato ad almeno un intervento.")
            return

        cur.execute("SELECT 1 FROM interventi_ricorrenti WHERE cliente_id = ? LIMIT 1", (cliente_id,))
        if cur.fetchone():
            QMessageBox.warning(self.ui, "Impossibile eliminare",
                                "Non puoi eliminare il cliente perché è associato ad almeno un intervento ricorrente.")
            return

        risposta = QMessageBox.question(
            self.ui,
            "Conferma eliminazione",
            "Sei sicuro di voler eliminare questo cliente?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if risposta != QMessageBox.StandardButton.Yes:
            return

        cur.execute("DELETE FROM clienti WHERE id = ?", (cliente_id,))
        conn.commit()
        self.load_clienti()

    # ---------------------------------------------------------
    #  GESTIONE SELEZIONE
    # ---------------------------------------------------------
    def on_selection_changed(self):
        ha_selezione = self.ui.tableClienti.currentRow() >= 0
        self.ui.btnClienteModifica.setEnabled(ha_selezione)
        self.ui.btnClienteElimina.setEnabled(ha_selezione)
