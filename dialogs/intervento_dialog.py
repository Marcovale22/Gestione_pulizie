from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QComboBox,
    QDateEdit, QTimeEdit, QDoubleSpinBox, QLineEdit,
    QDialogButtonBox, QMessageBox, QListWidget, QListWidgetItem, QAbstractItemView
)
from PyQt6.QtCore import QDate, QTime, Qt

from models.cliente import Cliente
from models.dipendenti import Dipendente
from models.servizi import Servizio




class InterventoDialog(QDialog):
    def __init__(self, parent=None, intervento=None):
        super().__init__(parent)
        self._dati = None

        self.setWindowTitle("Intervento")

        # --- campi ---
        self.comboCliente = QComboBox()
        self.comboServizio = QComboBox()
        self.listDipendenti = QListWidget()
        self.listDipendenti.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)

        self.comboStato = QComboBox()
        self.comboStato.addItems(["Programmato", "Completato", "Annullato"])

        self.dateData = QDateEdit()
        self.dateData.setCalendarPopup(True)
        self.dateData.setDate(QDate.currentDate())

        self.timeOra = QTimeEdit()
        self.timeOra.setTime(QTime.currentTime())

        self.spinDurata = QDoubleSpinBox()
        self.spinDurata.setRange(0, 24)
        self.spinDurata.setDecimals(2)

        self.editNote = QLineEdit()

        # popolamento combo da DB
        self._load_combo()

        form = QFormLayout()
        form.addRow("Cliente:", self.comboCliente)
        form.addRow("Servizio:", self.comboServizio)
        form.addRow("Dipendenti:", self.listDipendenti)
        form.addRow("Data:", self.dateData)
        form.addRow("Ora inizio:", self.timeOra)
        form.addRow("Durata (ore):", self.spinDurata)
        form.addRow("Stato:", self.comboStato)
        form.addRow("Note:", self.editNote)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(buttons)
        self.setLayout(layout)

        # modifica: precompilo
        if intervento is not None:
            self.setWindowTitle("Modifica intervento")
            self.set_dati(intervento)
        else:
            self.setWindowTitle("Aggiungi intervento")

    def _load_combo(self):
        # Clienti
        self.comboCliente.clear()
        clienti = Cliente.all()
        for c in clienti:
            self.comboCliente.addItem(f"{c.cognome} {c.nome}", c.id)

        # Servizi
        self.comboServizio.clear()
        servizi = Servizio.all()
        for s in servizi:
            self.comboServizio.addItem(s.nome, s.id)

        # Dipendenti
        self.listDipendenti.clear()
        dipendenti = Dipendente.all()
        for d in dipendenti:
            item = QListWidgetItem(f"{d.cognome} {d.nome}")
            item.setData(Qt.ItemDataRole.UserRole, d.id)
            self.listDipendenti.addItem(item)

    def _select_by_data(self, combo: QComboBox, value):
        for i in range(combo.count()):
            if combo.itemData(i) == value:
                combo.setCurrentIndex(i)
                return

    def set_dati(self, x: dict):
        # x contiene id (cliente_id, servizio_id, dipendente_id, ...)
        self._select_by_data(self.comboCliente, x.get("cliente_id"))
        self._select_by_data(self.comboServizio, x.get("servizio_id"))


        # data/ora
        try:
            y, m, d = map(int, x.get("data", "").split("-"))
            self.dateData.setDate(QDate(y, m, d))
        except:
            pass

        try:
            hh, mm = map(int, x.get("ora_inizio", "09:00").split(":"))
            self.timeOra.setTime(QTime(hh, mm))
        except:
            pass

        # durata
        try:
            self.spinDurata.setValue(float(x.get("durata_ore") or 0))
        except:
            self.spinDurata.setValue(0)

        # stato
        stato = x.get("stato", "Programmato")
        idx = self.comboStato.findText(stato)
        if idx >= 0:
            self.comboStato.setCurrentIndex(idx)

        self.editNote.setText(x.get("note", "") or "")

        ids = x.get("dipendente_ids")
        if ids is None:
            old = x.get("dipendente_id")
            ids = [] if old is None else [old]

        ids = set(ids)

        for i in range(self.listDipendenti.count()):
            item = self.listDipendenti.item(i)
            did = item.data(Qt.ItemDataRole.UserRole)
            item.setSelected(did in ids)

    def _on_accept(self):
        if self.comboCliente.count() == 0:
            QMessageBox.warning(self, "Dati mancanti", "Inserisci prima almeno un cliente.")
            return
        if self.comboServizio.count() == 0:
            QMessageBox.warning(self, "Dati mancanti", "Inserisci prima almeno un servizio.")
            return

        dip_ids = []
        for item in self.listDipendenti.selectedItems():
            dip_ids.append(item.data(Qt.ItemDataRole.UserRole))


        self._dati = {
            "cliente_id": self.comboCliente.currentData(),
            "servizio_id": self.comboServizio.currentData(),
            "data": self.dateData.date().toString("yyyy-MM-dd"),
            "ora_inizio": self.timeOra.time().toString("HH:mm"),
            "durata_ore": float(self.spinDurata.value()) if self.spinDurata.value() > 0 else None,
            "stato": self.comboStato.currentText(),
            "note": self.editNote.text().strip() or None,
            "dipendente_ids": dip_ids
        }

        self.accept()

    def get_dati(self) -> dict:
        return self._dati
