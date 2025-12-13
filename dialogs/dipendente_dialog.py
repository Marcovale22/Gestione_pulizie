from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit,
    QSpinBox, QDoubleSpinBox, QDateEdit,
    QDialogButtonBox, QMessageBox
)
from PyQt6.QtCore import QDate


class DipendenteDialog(QDialog):
    def __init__(self, parent=None, dipendente=None):
        super().__init__(parent)

        self.setWindowTitle("Dipendente")

        # ---- Campi ----
        self.edit_nome = QLineEdit()
        self.edit_cognome = QLineEdit()
        self.edit_telefono = QLineEdit()
        self.edit_email = QLineEdit()
        self.edit_mansione = QLineEdit()

        self.spin_ore = QSpinBox()
        self.spin_ore.setRange(0, 60)

        self.double_stipendio = QDoubleSpinBox()
        self.double_stipendio.setRange(0, 10000)
        self.double_stipendio.setDecimals(2)

        self.date_scadenza = QDateEdit()
        self.date_scadenza.setCalendarPopup(True)
        self.date_scadenza.setDate(QDate.currentDate())

        # ---- Layout form ----
        form = QFormLayout()
        form.addRow("Nome:", self.edit_nome)
        form.addRow("Cognome:", self.edit_cognome)
        form.addRow("Telefono:", self.edit_telefono)
        form.addRow("Email:", self.edit_email)
        form.addRow("Mansione:", self.edit_mansione)
        form.addRow("Ore settimanali:", self.spin_ore)
        form.addRow("Stipendio (€):", self.double_stipendio)
        form.addRow("Scadenza contratto:", self.date_scadenza)

        # ---- Pulsanti OK / Annulla ----
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(buttons)
        self.setLayout(layout)

        # Se sto modificando → precompilo
        if dipendente is not None:
            self.set_dati(dipendente)
            self.setWindowTitle("Modifica dipendente")

    # ------------------------------------------------------------------
    # Carico i dati nel dialog (per MODIFICA)
    # ------------------------------------------------------------------
    def set_dati(self, d: dict):
        self.edit_nome.setText(d.get("nome", ""))
        self.edit_cognome.setText(d.get("cognome", ""))
        self.edit_telefono.setText(d.get("telefono", ""))
        self.edit_email.setText(d.get("email", ""))
        self.edit_mansione.setText(d.get("mansione", ""))

        # campi numerici
        try:
            self.spin_ore.setValue(int(d.get("ore_settimanali") or 0))
        except:
            self.spin_ore.setValue(0)

        try:
            self.double_stipendio.setValue(float(d.get("stipendio") or 0.0))
        except:
            self.double_stipendio.setValue(0.0)

        # Data in formato YYYY-MM-DD
        data_str = d.get("scadenza_contratto")
        if data_str:
            try:
                y, m, day = map(int, data_str.split("-"))
                self.date_scadenza.setDate(QDate(y, m, day))
            except:
                pass

    # ------------------------------------------------------------------
    # VALIDAZIONE E RACCOLTA DATI
    # ------------------------------------------------------------------
    def _on_accept(self):
        nome = self.edit_nome.text().strip()
        cognome = self.edit_cognome.text().strip()

        if not nome or not cognome:
            QMessageBox.warning(
                self,
                "Dati mancanti",
                "Nome e cognome sono obbligatori."
            )
            return

        # Converto la data a formato YYYY-MM-DD
        data_q = self.date_scadenza.date()
        data_str = data_q.toString("yyyy-MM-dd")

        self._dati = {
            "nome": nome,
            "cognome": cognome,
            "telefono": self.edit_telefono.text().strip() or None,
            "email": self.edit_email.text().strip() or None,
            "mansione": self.edit_mansione.text().strip() or None,
            "ore_settimanali": self.spin_ore.value(),
            "stipendio": self.double_stipendio.value(),
            "scadenza_contratto": data_str,
        }

        self.accept()

    # ------------------------------------------------------------------
    # Getter dei dati, come ClienteDialog
    # ------------------------------------------------------------------
    def get_dati(self) -> dict:
        return getattr(self, "_dati", None)
