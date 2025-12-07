
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QDialogButtonBox,
)


class ClienteDialog(QDialog):
    def __init__(self, parent=None, cliente=None):
        super().__init__(parent)

        self.setWindowTitle("Cliente")

        # ---- campi ----
        self.edit_nome = QLineEdit()
        self.edit_cognome = QLineEdit()
        self.edit_telefono = QLineEdit()
        self.edit_indirizzo = QLineEdit()
        self.edit_email = QLineEdit()

        form = QFormLayout()
        form.addRow("Nome:", self.edit_nome)
        form.addRow("Cognome:", self.edit_cognome)
        form.addRow("Telefono:", self.edit_telefono)
        form.addRow("Indirizzo:", self.edit_indirizzo)
        form.addRow("Email:", self.edit_email)

        # ---- pulsanti OK / Annulla ----
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(buttons)

        self.setLayout(layout)

        # se passo un cliente, precompilo i campi
        if cliente is not None:
            self.set_dati(cliente)

    def set_dati(self, cliente: dict):
        """cliente è un dict con le chiavi: nome, cognome, telefono, indirizzo, email"""
        self.edit_nome.setText(cliente.get("nome", ""))
        self.edit_cognome.setText(cliente.get("cognome", ""))
        self.edit_telefono.setText(cliente.get("telefono", ""))
        self.edit_indirizzo.setText(cliente.get("indirizzo", ""))
        self.edit_email.setText(cliente.get("email", ""))

    def get_dati(self) -> dict:
        """Ritorna i dati inseriti nella dialog."""
        return {
            "nome": self.edit_nome.text().strip(),
            "cognome": self.edit_cognome.text().strip(),
            "telefono": self.edit_telefono.text().strip(),
            "indirizzo": self.edit_indirizzo.text().strip(),
            "email": self.edit_email.text().strip(),
        }
