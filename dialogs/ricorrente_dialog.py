from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QComboBox,
    QTimeEdit, QDoubleSpinBox, QLineEdit, QDialogButtonBox,
    QMessageBox, QListWidget, QListWidgetItem, QAbstractItemView,
    QCheckBox, QSpinBox
)
from PyQt6.QtCore import QTime, Qt

from models.cliente import Cliente
from models.dipendenti import Dipendente
from models.servizi import Servizio


GIORNI = [
    (1, "Lun"), (2, "Mar"), (3, "Mer"), (4, "Gio"), (5, "Ven"), (6, "Sab"), (7, "Dom")
]


class RicorrenteDialog(QDialog):
    def __init__(self, parent=None, ricorrente=None):
        super().__init__(parent)
        self._dati = None

        self.comboCliente = QComboBox()
        self.comboServizio = QComboBox()

        self.timeOra = QTimeEdit()
        self.timeOra.setTime(QTime.currentTime())

        self.spinDurata = QDoubleSpinBox()
        self.spinDurata.setRange(0, 24)
        self.spinDurata.setDecimals(2)

        self.editNote = QLineEdit()

        self.chkAttivo = QCheckBox("Attivo")
        self.chkAttivo.setChecked(True)

        self.listGiorni = QListWidget()
        self.listGiorni.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)

        self.listDipendenti = QListWidget()
        self.listDipendenti.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)

        self.spinGenera = QSpinBox()
        self.spinGenera.setRange(0, 52)     # 0 = non generare
        self.spinGenera.setValue(0)

        self._load()

        form = QFormLayout()
        form.addRow("Cliente:", self.comboCliente)
        form.addRow("Servizio:", self.comboServizio)
        form.addRow("Ora inizio:", self.timeOra)
        form.addRow("Durata (ore):", self.spinDurata)
        form.addRow("Giorni:", self.listGiorni)
        form.addRow("Dipendenti:", self.listDipendenti)
        form.addRow("", self.chkAttivo)
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

        if ricorrente is not None:
            self.setWindowTitle("Modifica ricorrente")
            self.set_dati(ricorrente)
        else:
            self.setWindowTitle("Aggiungi ricorrente")

    def _load(self):
        # clienti
        self.comboCliente.clear()
        for c in Cliente.all():
            self.comboCliente.addItem(f"{c.cognome} {c.nome}", c.id)

        # servizi
        self.comboServizio.clear()
        for s in Servizio.all():
            self.comboServizio.addItem(s.nome, s.id)

        # giorni
        self.listGiorni.clear()
        for g_id, g_name in GIORNI:
            item = QListWidgetItem(g_name)
            item.setData(Qt.ItemDataRole.UserRole, g_id)
            self.listGiorni.addItem(item)

        # dipendenti
        self.listDipendenti.clear()
        for d in Dipendente.all():
            item = QListWidgetItem(f"{d.cognome} {d.nome}")
            item.setData(Qt.ItemDataRole.UserRole, d.id)
            self.listDipendenti.addItem(item)

    def _select_by_data(self, combo: QComboBox, value):
        for i in range(combo.count()):
            if combo.itemData(i) == value:
                combo.setCurrentIndex(i)
                return

    def set_dati(self, x: dict):
        self._select_by_data(self.comboCliente, x.get("cliente_id"))
        self._select_by_data(self.comboServizio, x.get("servizio_id"))

        # ora
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

        self.editNote.setText(x.get("note", "") or "")
        self.chkAttivo.setChecked(bool(x.get("attivo", 1)))

        # giorni selezionati
        giorni = set(x.get("giorni_settimana", []))
        for i in range(self.listGiorni.count()):
            item = self.listGiorni.item(i)
            g = item.data(Qt.ItemDataRole.UserRole)
            item.setSelected(g in giorni)

        # dipendenti selezionati
        dip_ids = set(x.get("dipendente_ids", []))
        for i in range(self.listDipendenti.count()):
            item = self.listDipendenti.item(i)
            did = item.data(Qt.ItemDataRole.UserRole)
            item.setSelected(did in dip_ids)

        # su modifica, di default non rigenero a meno che lo scegli tu
        self.spinGenera.setValue(0)

    def _on_accept(self):
        if self.comboCliente.count() == 0:
            QMessageBox.warning(self, "Dati mancanti", "Inserisci prima almeno un cliente.")
            return
        if self.comboServizio.count() == 0:
            QMessageBox.warning(self, "Dati mancanti", "Inserisci prima almeno un servizio.")
            return
        if len(self.listGiorni.selectedItems()) == 0:
            QMessageBox.warning(self, "Dati mancanti", "Seleziona almeno un giorno della settimana.")
            return

        giorni = [it.data(Qt.ItemDataRole.UserRole) for it in self.listGiorni.selectedItems()]
        dip_ids = [it.data(Qt.ItemDataRole.UserRole) for it in self.listDipendenti.selectedItems()]

        self._dati = {
            "cliente_id": self.comboCliente.currentData(),
            "servizio_id": self.comboServizio.currentData(),
            "ora_inizio": self.timeOra.time().toString("HH:mm"),
            "durata_ore": float(self.spinDurata.value()) if self.spinDurata.value() > 0 else None,
            "note": self.editNote.text().strip() or None,
            "attivo": self.chkAttivo.isChecked(),
            "giorni_settimana": giorni,
            "dipendente_ids": dip_ids,
        }
        self.accept()

    def get_dati(self) -> dict:
        return self._dati
