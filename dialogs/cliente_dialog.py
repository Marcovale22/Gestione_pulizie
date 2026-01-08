from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QDialogButtonBox,
    QMessageBox,
    QLabel
)

class ClienteDialog(QDialog):
    def __init__(self, parent=None, cliente=None):
        super().__init__(parent)

        self.setWindowTitle("Cliente")

        self.edit_nome = QLineEdit()
        self.edit_cognome = QLineEdit()
        self.edit_telefono = QLineEdit()
        self.edit_indirizzo = QLineEdit()
        self.edit_email = QLineEdit()

        form = QFormLayout()

        #  asterischi sui campi obbligatori
        form.addRow("Nome <font color='red'>*</font>:", self.edit_nome)
        form.addRow("Cognome <font color='red'>*</font>:", self.edit_cognome)
        form.addRow("Telefono:", self.edit_telefono)
        form.addRow("Indirizzo:", self.edit_indirizzo)
        form.addRow("Email:", self.edit_email)

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )

        self.buttons.button(QDialogButtonBox.StandardButton.Ok).clicked.connect(self.on_ok)
        self.buttons.rejected.connect(self.reject)

        # legenda in fondo
        lbl_obbl = QLabel("<font color='red'>*</font> Campo obbligatorio")
        lbl_obbl.setStyleSheet("font-size: 11px;")

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(lbl_obbl)
        layout.addWidget(self.buttons)
        self.setLayout(layout)

        if cliente is not None:
            self.set_dati(cliente)

    def on_ok(self):
        nome = self.edit_nome.text().strip()
        cognome = self.edit_cognome.text().strip()

        if not nome or not cognome:
            QMessageBox.warning(self, "Dati mancanti", "Nome e cognome sono obbligatori.")
            return

        super().accept()

    def set_dati(self, cliente: dict):
        self.edit_nome.setText(cliente.get("nome", ""))
        self.edit_cognome.setText(cliente.get("cognome", ""))
        self.edit_telefono.setText(cliente.get("telefono", ""))
        self.edit_indirizzo.setText(cliente.get("indirizzo", ""))
        self.edit_email.setText(cliente.get("email", ""))

    def get_dati(self) -> dict:
        return {
            "nome": self.edit_nome.text().strip(),
            "cognome": self.edit_cognome.text().strip(),
            "telefono": self.edit_telefono.text().strip(),
            "indirizzo": self.edit_indirizzo.text().strip(),
            "email": self.edit_email.text().strip(),
        }
