from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QComboBox,
    QTimeEdit, QDoubleSpinBox, QDialogButtonBox, QMessageBox,
    QListWidget, QListWidgetItem, QAbstractItemView, QCheckBox, QWidget, QHBoxLayout
)
from PyQt6.QtCore import QTime, Qt

from models.cliente import Cliente
from models.dipendenti import Dipendente
from models.servizi import Servizio


class RicorrenteDialog(QDialog):
    def __init__(self, parent=None, ricorrente=None):
        super().__init__(parent)
        self._dati = None

        self.setWindowTitle("Ricorrente")

        # --- campi ---
        self.comboCliente = QComboBox()
        self.comboServizio = QComboBox()

        self.listDipendenti = QListWidget()
        self.listDipendenti.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)

        self.timeOra = QTimeEdit()
        self.timeOra.setTime(QTime.currentTime())

        self.timeDurata = QTimeEdit()
        self.timeDurata.setDisplayFormat("HH:mm")
        self.timeDurata.setTime(QTime(0, 0))  # durata iniziale

        self.chkAttivo = QCheckBox("Attivo")
        self.chkAttivo.setChecked(True)

        # Giorni settimana (checkbox)
        self.chk = {}
        giorni = [("Lun", 1), ("Mar", 2), ("Mer", 3), ("Gio", 4), ("Ven", 5), ("Sab", 6), ("Dom", 7)]
        giorni_widget = QWidget()
        giorni_layout = QHBoxLayout(giorni_widget)
        giorni_layout.setContentsMargins(0, 0, 0, 0)
        for label, val in giorni:
            c = QCheckBox(label)
            self.chk[val] = c
            giorni_layout.addWidget(c)

        # popolo da DB
        self._load_combo()

        form = QFormLayout()
        form.addRow("Cliente:", self.comboCliente)
        form.addRow("Servizio:", self.comboServizio)
        form.addRow("Dipendenti:", self.listDipendenti)
        form.addRow("Giorni:", giorni_widget)
        form.addRow("Ora inizio:", self.timeOra)
        form.addRow("Durata:", self.timeDurata)   # ✅ label pulita
        form.addRow("Stato:", self.chkAttivo)

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

    def _load_combo(self):
        # Clienti
        self.comboCliente.clear()
        for c in Cliente.all():
            self.comboCliente.addItem(f"{c.cognome} {c.nome}", c.id)

        # Servizi
        self.comboServizio.clear()
        for s in Servizio.all():
            self.comboServizio.addItem(s.nome, s.id)

        # Dipendenti
        self.listDipendenti.clear()
        for d in Dipendente.all():
            it = QListWidgetItem(f"{d.cognome} {d.nome}")
            it.setData(Qt.ItemDataRole.UserRole, d.id)
            self.listDipendenti.addItem(it)

    def _select_by_data(self, combo: QComboBox, value):
        for i in range(combo.count()):
            if combo.itemData(i) == value:
                combo.setCurrentIndex(i)
                return

    def set_dati(self, r: dict):
        self._select_by_data(self.comboCliente, r.get("cliente_id"))
        self._select_by_data(self.comboServizio, r.get("servizio_id"))

        # ora
        try:
            hh, mm = map(int, (r.get("ora_inizio") or "09:00").split(":"))
            self.timeOra.setTime(QTime(hh, mm))
        except:
            pass

        # durata
        try:
            ore = float(r.get("durata_ore") or 0.0)
            total_min = int(round(ore * 60))
            h = total_min // 60
            m = total_min % 60
            self.timeDurata.setTime(QTime(h, m))
        except:
            self.timeDurata.setTime(QTime(0, 0))

        # attivo
        self.chkAttivo.setChecked(bool(r.get("attivo", 1)))

        # giorni
        giorni = set(r.get("giorni_settimana") or [])
        for val, cb in self.chk.items():
            cb.setChecked(val in giorni)

        # dipendenti selezionati
        ids = set(r.get("dipendente_ids") or [])
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

        # giorni obbligatori (almeno 1)
        giorni_sel = [val for val, cb in self.chk.items() if cb.isChecked()]
        if not giorni_sel:
            QMessageBox.warning(self, "Dati mancanti", "Seleziona almeno un giorno della settimana.")
            return

        t = self.timeDurata.time()
        durata = (t.hour() * 60 + t.minute()) / 60.0

        if durata <= 0:
            QMessageBox.warning(self, "Dati mancanti", "La durata è obbligatoria (es. 00:30).")
            return

        dip_ids = [item.data(Qt.ItemDataRole.UserRole) for item in self.listDipendenti.selectedItems()]

        self._dati = {
            "cliente_id": self.comboCliente.currentData(),
            "servizio_id": self.comboServizio.currentData(),
            "ora_inizio": self.timeOra.time().toString("HH:mm"),
            "durata_ore": durata,
            "attivo": 1 if self.chkAttivo.isChecked() else 0,
            "giorni_settimana": giorni_sel,
            "dipendente_ids": dip_ids
        }

        self.accept()

    def get_dati(self) -> dict:
        return self._dati
