from PyQt6.QtWidgets import QTableWidgetItem, QHeaderView
from models.cliente import Cliente


class ClientiSection:
    def __init__(self, ui):
        """
        ui è la Ui_MainWindow vera (non MainWindow).
        Contiene tableClienti, btnClienteAggiungi, ecc.
        """
        self.ui = ui
        self.setup_table()
        self.setup_signals()
        self.load_clienti()

    # ---------------------------------------------------------
    #  SETUP TABELLA
    # ---------------------------------------------------------
    def setup_table(self):
        table = self.ui.tableClienti

        # colonne
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels([
            "Nome", "Cognome", "Telefono", "Indirizzo", "Email"
        ])

        header = table.horizontalHeader()

        # gestisce automaticamente lo spazio disponibile
        header.setStretchLastSection(True)

        # permette lo scroll orizzontale quando la finestra è troppo piccola
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

        # righe alternate
        table.setAlternatingRowColors(True)

        # rimuove numeri riga
        table.verticalHeader().setVisible(False)

        # se vuoi visibile la griglia
        table.setShowGrid(True)

        # evita che il contenuto stringa la tabella troppo
        table.setWordWrap(False)

        # scrollbar abilitate in automatico
        table.setHorizontalScrollMode(table.ScrollMode.ScrollPerPixel)
        table.setVerticalScrollMode(table.ScrollMode.ScrollPerPixel)


    def setup_signals(self):
            self.ui.btnClienteAggiungi.clicked.connect(self.aggiungi_cliente)

            # ---------------------------------------------------------
            #  CARICAMENTO DATI
            # ---------------------------------------------------------

    def load_clienti(self):
        clienti = Cliente.all()
        table = self.ui.tableClienti

        table.setRowCount(len(clienti))

        for row_idx, cliente in enumerate(clienti):
            table.setItem(row_idx, 0, QTableWidgetItem(cliente.nome))
            table.setItem(row_idx, 1, QTableWidgetItem(cliente.cognome))
            table.setItem(row_idx, 2, QTableWidgetItem(cliente.telefono or ""))
            table.setItem(row_idx, 3, QTableWidgetItem(cliente.indirizzo or ""))
            table.setItem(row_idx, 4, QTableWidgetItem(cliente.email or ""))

            # ---------------------------------------------------------
            #  TASTO AGGIUNGI
            # ---------------------------------------------------------


    def aggiungi_cliente(self):
            print("TODO: aggiungi cliente")