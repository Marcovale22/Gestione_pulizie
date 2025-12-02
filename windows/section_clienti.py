from PyQt6.QtWidgets import QTableWidgetItem, QHeaderView
from models.cliente import Cliente
from database.database import get_connection


class ClientiSection:
    def __init__(self, ui):
        self.ui = ui
        self.setup_table()
        self.setup_signals()
        self.load_clienti()

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

    # ---------------------------------------------------------
    #  SIGNALS
    # ---------------------------------------------------------
    def setup_signals(self):
        self.ui.btnClienteAggiungi.clicked.connect(self.aggiungi_cliente)
        self.ui.btnClienteModifica.clicked.connect(self.modifica_cliente)
        self.ui.btnClienteElimina.clicked.connect(self.elimina_cliente)

    # ---------------------------------------------------------
    #  CARICAMENTO DATI
    # ---------------------------------------------------------
    def load_clienti(self):
        table = self.ui.tableClienti
        clienti = Cliente.all()

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

    # ---------------------------------------------------------
    #  AGGIUNGI CLIENTE (DA IMPLEMENTARE)
    # ---------------------------------------------------------
    def aggiungi_cliente(self):
        print("TODO: aggiungi cliente")

    # ---------------------------------------------------------
    #  MODIFICA CLIENTE
    # ---------------------------------------------------------
    def modifica_cliente(self):
        table = self.ui.tableClienti
        row = table.currentRow()

        if row < 0:
            print("Nessun cliente selezionato")
            return

        cliente_id = table.item(row, 0).text()
        nome = table.item(row, 1).text()
        cognome = table.item(row, 2).text()
        telefono = table.item(row, 3).text()
        indirizzo = table.item(row, 4).text()
        email = table.item(row, 5).text()

        print("MODIFICA:", cliente_id, nome, cognome, telefono, indirizzo, email)

    # ---------------------------------------------------------
    #  ELIMINA CLIENTE
    # ---------------------------------------------------------
    def elimina_cliente(self):
        table = self.ui.tableClienti
        row = table.currentRow()

        if row < 0:
            print("Nessun cliente selezionato per l'eliminazione")
            return

        cliente_id = int(table.item(row, 0).text())

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM clienti WHERE id = ?", (cliente_id,))
        conn.commit()

        print(f"Cliente ID {cliente_id} eliminato")
        self.load_clienti()
