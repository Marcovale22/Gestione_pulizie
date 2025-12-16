import os
from PyQt6.QtWidgets import QMainWindow
from PyQt6.uic import loadUi
from PyQt6.QtGui import QPixmap

from windows.dipendenti_section import DipendentiSection
from windows.clienti_section import ClientiSection
from windows.servizi_section import ServiziSection
from windows.interventi_section import InterventiSection
from windows.calendario_section import CalendarioSection


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()



        base_dir = os.path.dirname(os.path.dirname(__file__))
        ui_path = os.path.join(base_dir, "ui", "main_window.ui")
        loadUi(ui_path, self)

        # --- LOGO ---
        logo_path = os.path.join(base_dir, "assets", "logo_brilance.png")
        pixmap = QPixmap(logo_path)
        self.lblLogo.setPixmap(pixmap)
        self.lblLogo.setScaledContents(True)  # adatta l'immagine alla label

        # Rendo i pulsanti della sidebar "checkable"
        self.btn_list = [
            self.btnAreaClienti,
            self.btnAreaDipendenti,
            self.btnAreaServizi,
            self.btnAreaInterventi,
            self.btnCalendario
        ]
        for btn in self.btn_list:
            btn.setCheckable(True)

        # Collega i pulsanti della sidebar alle pagine dello stacked
        self.btnAreaClienti.clicked.connect(lambda: self.select_section(0, self.btnAreaClienti))
        self.btnAreaDipendenti.clicked.connect(lambda: self.select_section(1, self.btnAreaDipendenti))
        self.btnAreaServizi.clicked.connect(lambda: self.select_section(2, self.btnAreaServizi))
        self.btnAreaInterventi.clicked.connect(lambda: self.select_section(3, self.btnAreaInterventi))
        self.btnCalendario.clicked.connect(lambda: self.select_section(4, self.btnCalendario))

        # Sezioni
        self.clienti_section = ClientiSection(self)
        self.dipendenti_section = DipendentiSection(self)
        self.servizi_section = ServiziSection(self)
        self.interventi_section = InterventiSection(self)
        self.calendario_section = CalendarioSection(self)

        # Imposto la pagina iniziale e il pulsante selezionato
        self.select_section(0, self.btnAreaClienti)

    # ---------- METODI DI SUPPORTO ----------

    def uncheck_all(self):
        for btn in self.btn_list:
            btn.setChecked(False)

    def select_section(self, index, btn):
        self.uncheck_all()
        btn.setChecked(True)
        self.stackedContent.setCurrentIndex(index)

        if index == 4:
            self.calendario_section.refresh_calendar()


