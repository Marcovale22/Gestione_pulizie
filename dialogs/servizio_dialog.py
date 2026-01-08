from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit,
    QDoubleSpinBox, QDialogButtonBox, QMessageBox, QLabel
)


class ServizioDialog(QDialog):
    def __init__(self, parent=None, servizio=None):
        super().__init__(parent)
        self.setWindowTitle("Servizio")

        self.edit_nome = QLineEdit()
        self.edit_descrizione = QLineEdit()

        self.double_prezzo = QDoubleSpinBox()
        self.double_prezzo.setRange(0, 10000)
        self.double_prezzo.setDecimals(2)

        form = QFormLayout()

        # asterisco sui campi obbligatori
        form.addRow("Nome <font color='red'>*</font>:", self.edit_nome)
        form.addRow("Descrizione:", self.edit_descrizione)
        form.addRow("Prezzo mensile (€) <font color='red'>*</font>:", self.double_prezzo)

        #  legenda in fondo
        lbl_obbl = QLabel("<font color='red'>*</font> Campo obbligatorio")
        lbl_obbl.setStyleSheet("font-size: 11px;")

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(lbl_obbl)   # sotto il form
        layout.addWidget(buttons)
        self.setLayout(layout)

        self._dati = None

        if servizio is not None:
            self.setWindowTitle("Modifica servizio")
            self.set_dati(servizio)
        else:
            self.setWindowTitle("Aggiungi servizio")

    def set_dati(self, servizio: dict):
        self.edit_nome.setText(servizio.get("nome", ""))
        self.edit_descrizione.setText(servizio.get("descrizione", ""))

        try:
            self.double_prezzo.setValue(float(servizio.get("prezzo_mensile") or 0.0))
        except:
            self.double_prezzo.setValue(0.0)

    def _on_accept(self):
        nome = self.edit_nome.text().strip()
        if not nome:
            QMessageBox.warning(self, "Dati mancanti", "Il nome del servizio è obbligatorio.")
            return

        prezzo = float(self.double_prezzo.value())
        if prezzo <= 0:
            QMessageBox.warning(self, "Dati mancanti", "Il prezzo mensile è obbligatorio e deve essere > 0.")
            return

        self._dati = {
            "nome": nome,
            "descrizione": self.edit_descrizione.text().strip() or None,
            "prezzo_mensile": prezzo
        }
        self.accept()

    def get_dati(self) -> dict:
        return self._dati
