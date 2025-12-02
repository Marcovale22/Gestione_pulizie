from PyQt6.QtWidgets import QTableWidgetItem, QHeaderView
from models.cliente import Cliente


class ClientiSection:
    def __init__(self, ui):
        """
        ui è la MainWindow: contiene tableClienti, btnClienteAggiungi, ecc.
        """
        self.ui = ui

        self.setup_table()
        self.setup_signals()
        self.load_clienti()

    def setup_table(self):
        table = self.ui.tableClienti

        # 5 colonne: Nome, Cognome, Telefono, Indirizzo, Email
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels([
            "Nome", "Cognome", "Telefono", "Indirizzo", "Email"
        ])

        header = table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        #numeri a fianco le righe
        table.verticalHeader().setVisible(False)

        table.setShowGrid(True)
        table.setAlternatingRowColors(True)

    def setup_signals(self):
        self.ui.btnClienteAggiungi.clicked.connect(self.aggiungi_cliente)
        # le altre le colleghiamo dopo
        # self.ui.btnClienteModifica.clicked.connect(self.modifica_cliente)
        # self.ui.btnClienteElimina.clicked.connect(self.elimina_cliente)

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

    def aggiungi_cliente(self):
        # per ora solo debug, poi ci mettiamo la finestra di inserimento
        print("TODO: aggiungi cliente")
