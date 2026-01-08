from PyQt6.QtCore import Qt, QDate, QEvent, QObject
from PyQt6.QtWidgets import QHeaderView, QAbstractItemView, QTableWidgetItem, QMessageBox, QCalendarWidget, QToolTip, QTableView
from PyQt6.QtGui import QTextCharFormat, QColor

from database.repositories.interventi_repo import get_interventi_misti
from widgets.brillance_calendar import BrillanceCalendar

class CalendarioSection(QObject):
    def __init__(self, ui):
        super().__init__()
        self.ui = ui
        self.events_by_date = {}
        self.setup_calendar()
        self.setup_table()
        self.setup_signals()

        self.ui.stackedContent.setCurrentWidget(self.ui.pageCalendario)
        self.selected_date = QDate.currentDate()

        # applica formati iniziali (oggi + fuori mese grigi)
        self.refresh_calendar_formats()

    # ---------------- CALENDARIO ----------------
    def setup_calendar(self):
        cal = self.ui.tableGiorno  # QCalendarWidget

        if not isinstance(cal, BrillanceCalendar):
            parent = cal.parent()
            layout = parent.layout()

            new_cal = BrillanceCalendar(parent)
            new_cal.setObjectName(cal.objectName())  # mantiene lo stesso nome
            new_cal.setGridVisible(cal.isGridVisible())
            new_cal.setSelectedDate(cal.selectedDate())

            # rimpiazza nel layout
            if layout is not None:
                layout.replaceWidget(cal, new_cal)
            cal.deleteLater()

            # aggiorna il riferimento in ui
            self.ui.tableGiorno = new_cal
            cal = new_cal
        # togli numeri settimane a sinistra
        cal.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)

        # seleziona oggi
        cal.setSelectedDate(QDate.currentDate())

        self.format_weekday_headers()
        # quando cambi mese/anno, riapplica formati
        cal.currentPageChanged.connect(lambda y, m: self.refresh_calendar_formats())

        self.install_calendar_tooltips()

        self.refresh_calendar_formats()

    def build_events_cache_for_month(self):
        cal = self.ui.tableGiorno
        year = cal.yearShown()
        month = cal.monthShown()

        rows = get_interventi_misti()
        self.events_by_date = {}  # QDate -> list[dict]

        def add_event(qd: QDate, ev: dict):
            self.events_by_date.setdefault(qd, []).append(ev)

        # range mese visibile (42 celle)
        first = QDate(year, month, 1)
        start_grid = first.addDays(-(first.dayOfWeek() - 1))


        for r in rows:
            tipo = r["tipo"]

            # ---------------- SINGOLO ----------------
            if tipo == "SINGOLO":
                data_iso = (r["data"] or "").strip()
                if not data_iso or data_iso == "-":
                    continue

                qd = QDate.fromString(data_iso, "yyyy-MM-dd")
                if not qd.isValid():
                    continue

                # opzionale: mostra solo il mese corrente (io lo consiglio)
                if qd.year() != year or qd.month() != month:
                    continue

                add_event(qd, {
                    "id_ref": r["id_ref"],
                    "tipo": "SINGOLO",
                    "ora": r["ora"],
                    "cliente": r["cliente"],
                    "servizio": r["servizio"],
                    "durata": r["durata"],
                    "stato": r["stato"],
                    "dipendenti": r["dipendenti"],
                })

                continue

            # ---------------- RICORRENTE ----------------
            if tipo == "RICORRENTE":
                # stato: Attivo/Sospeso (dalla query)
                if (r["stato"] or "").strip().lower() != "attivo":
                    continue

                # giorni: "1,3,5" ecc.
                giorni_csv = (r["giorni"] or "").strip()
                if not giorni_csv or giorni_csv == "-":
                    continue

                try:
                    weekdays = {int(x.strip()) for x in giorni_csv.split(",") if x.strip().isdigit()}
                except Exception:
                    continue

                # periodo: "YYYY-MM-DD → YYYY-MM-DD" oppure "- → -"
                periodo = (r["periodo"] or "").strip()
                data_inizio = None
                data_fine = None
                if "→" in periodo:
                    p1, p2 = [x.strip() for x in periodo.split("→", 1)]
                    if p1 != "-" and p1:
                        data_inizio = QDate.fromString(p1, "yyyy-MM-dd")
                        if not data_inizio.isValid():
                            data_inizio = None
                    if p2 != "-" and p2:
                        data_fine = QDate.fromString(p2, "yyyy-MM-dd")
                        if not data_fine.isValid():
                            data_fine = None

                # per ogni giorno nella griglia (42 celle), se è nel mese corrente e matcha weekday -> aggiungi
                for i in range(42):
                    d = start_grid.addDays(i)

                    # mostra solo giorni del mese corrente
                    if d.month() != month:
                        continue

                    # filtra per periodo (se presente)
                    if data_inizio and d < data_inizio:
                        continue
                    if data_fine and d > data_fine:
                        continue

                    if d.dayOfWeek() in weekdays:
                        add_event(d, {
                            "id_ref": r["id_ref"],
                            "tipo": "RICORRENTE",
                            "ora": r["ora"],
                            "cliente": r["cliente"],
                            "servizio": r["servizio"],
                            "durata": r["durata"],
                            "stato": r["stato"],
                            "dipendenti": r["dipendenti"],
                        })

        # ordina eventi per ora
        for qd, evs in self.events_by_date.items():
            evs.sort(key=lambda e: (e.get("ora") or ""))


    def date_from_cell(self, row: int, col: int) -> QDate:
        cal = self.ui.tableGiorno
        year = cal.yearShown()
        month = cal.monthShown()

        first = QDate(year, month, 1)
        start = first.addDays(-(first.dayOfWeek() - 1))  # lunedì prima riga

        return start.addDays(row * 7 + col)

    def install_calendar_tooltips(self):
        cal = self.ui.tableGiorno
        view = cal.findChild(QTableView)
        if view is not None:
            self._cal_view = view
            view.viewport().installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.ToolTip and hasattr(self, "_cal_view"):
            # assicuriamoci che l'evento arrivi dal viewport della tabella del calendario
            if obj is not self._cal_view.viewport():
                return False

            idx = self._cal_view.indexAt(event.pos())
            if not idx.isValid():
                QToolTip.hideText()
                return True

            d = self.date_from_cell(idx.row(), idx.column())
            evs = self.events_by_date.get(d, [])

            if evs:
                lines = [f"{d.toString('dd-MM-yyyy')}  •  {len(evs)} interventi"]
                for e in evs[:3]:
                    lines.append(f"• {e.get('ora', '')}  {e.get('cliente', '')} — {e.get('servizio', '')}")
                if len(evs) > 3:
                    lines.append("…")

                # ✅ PyQt6: globalPos() è più stabile di globalPosition()
                QToolTip.showText(event.globalPos(), "\n".join(lines), self.ui.tableGiorno)
            else:
                QToolTip.hideText()

            return True

        return False


    def refresh_calendar_formats(self):
        cal = self.ui.tableGiorno

        cal.setDateTextFormat(QDate(), QTextCharFormat())

        self.format_visible_cells()
        self.mark_holidays()

        self.build_events_cache_for_month()


        if hasattr(self.ui.tableGiorno, "setEvents"):
            self.ui.tableGiorno.setEvents(self.events_by_date)

        self.highlight_today()

    def reset_calendar_formats(self):
        # resetta i formati (Qt trick: data "null" resetta)
        self.ui.tableGiorno.setDateTextFormat(QDate(), QTextCharFormat())

    def refresh_calendar(self):
        self.refresh_calendar_formats()
        self.ui.tableGiorno.update()  # forza repaint

    def highlight_today(self):
        cal = self.ui.tableGiorno
        today = QDate.currentDate()

        fmt = QTextCharFormat()
        fmt.setBackground(QColor("#DBEAFE"))
        fmt.setForeground(QColor("#1D4ED8"))
        fmt.setFontWeight(600)

        cal.setDateTextFormat(today, fmt)

    def format_visible_cells(self):
        cal = self.ui.tableGiorno
        year = cal.yearShown()
        month = cal.monthShown()

        fmt_norm = QTextCharFormat()
        fmt_norm.setForeground(QColor("#111827"))  # nero

        fmt_weekend = QTextCharFormat()
        fmt_weekend.setForeground(QColor("#DC2626"))  # rosso

        fmt_other = QTextCharFormat()
        fmt_other.setForeground(QColor("#9CA3AF"))  # grigio

        # reset
        cal.setDateTextFormat(QDate(), QTextCharFormat())

        first = QDate(year, month, 1)
        start = first.addDays(-(first.dayOfWeek() - 1))  # lunedì prima riga

        for i in range(42):
            d = start.addDays(i)

            if d.month() != month:
                cal.setDateTextFormat(d, fmt_other)
            else:
                # sabato=6 domenica=7
                if d.dayOfWeek() in (6, 7):
                    cal.setDateTextFormat(d, fmt_weekend)
                else:
                    cal.setDateTextFormat(d, fmt_norm)

    def format_weekday_headers(self):
        cal = self.ui.tableGiorno

        fmt_week = QTextCharFormat()
        fmt_week.setForeground(QColor("#111827"))
        fmt_week.setFontWeight(700)

        fmt_weekend = QTextCharFormat()
        fmt_weekend.setForeground(QColor("#DC2626"))
        fmt_weekend.setFontWeight(700)

        cal.setWeekdayTextFormat(Qt.DayOfWeek.Monday, fmt_week)
        cal.setWeekdayTextFormat(Qt.DayOfWeek.Tuesday, fmt_week)
        cal.setWeekdayTextFormat(Qt.DayOfWeek.Wednesday, fmt_week)
        cal.setWeekdayTextFormat(Qt.DayOfWeek.Thursday, fmt_week)
        cal.setWeekdayTextFormat(Qt.DayOfWeek.Friday, fmt_week)

        cal.setWeekdayTextFormat(Qt.DayOfWeek.Saturday, fmt_weekend)
        cal.setWeekdayTextFormat(Qt.DayOfWeek.Sunday, fmt_weekend)

    def easter_sunday(self, year: int) -> QDate:
        """Calcola Pasqua (calendario gregoriano)"""
        a = year % 19
        b = year // 100
        c = year % 100
        d = b // 4
        e = b % 4
        f = (b + 8) // 25
        g = (b - f + 1) // 3
        h = (19 * a + b - d - g + 15) % 30
        i = c // 4
        k = c % 4
        l = (32 + 2 * e + 2 * i - h - k) % 7
        m = (a + 11 * h + 22 * l) // 451
        month = (h + l - 7 * m + 114) // 31
        day = ((h + l - 7 * m + 114) % 31) + 1
        return QDate(year, month, day)

    def italian_holidays(self, year: int) -> set[QDate]:
        fixed = {
            QDate(year, 1, 1),  # Capodanno
            QDate(year, 1, 6),  # Epifania
            QDate(year, 4, 25),  # Liberazione
            QDate(year, 5, 1),  # Festa del Lavoro
            QDate(year, 6, 2),  # Repubblica
            QDate(year, 8, 15),  # Ferragosto
            QDate(year, 11, 1),  # Ognissanti
            QDate(year, 12, 8),  # Immacolata
            QDate(year, 12, 25),  # Natale
            QDate(year, 12, 26),  # Santo Stefano
        }

        easter = self.easter_sunday(year)
        easter_monday = easter.addDays(1)

        return fixed | {easter, easter_monday}

    def mark_holidays(self):
        cal = self.ui.tableGiorno
        year = cal.yearShown()

        holidays = self.italian_holidays(year)

        fmt_holiday = QTextCharFormat()
        fmt_holiday.setForeground(QColor("#DC2626"))
        fmt_holiday.setFontWeight(700)

        # Applica SOLO se il giorno è nel mese mostrato (così i fuori-mese restano grigi)
        month = cal.monthShown()
        for d in holidays:
            if d.month() == month:
                cal.setDateTextFormat(d, fmt_holiday)

    # ---------------- TABELLA DETTAGLIO GIORNO ----------------
    def setup_table(self):
        table = self.ui.tableWidget

        table.setColumnCount(8)
        table.setHorizontalHeaderLabels([
            "ID_REF",
            "Tipo",
            "Ora",
            "Cliente",
            "Servizio",
            "Dipendenti",
            "Durata",
            "Stato"
        ])

        table.setColumnHidden(0, True)  # ID_REF

        header = table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

        table.setAlternatingRowColors(True)
        table.verticalHeader().setVisible(False)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        table.setShowGrid(True)
        table.setWordWrap(False)

        table.setStyleSheet(self.ui.tableClienti.styleSheet())

        # larghezze consigliate
        table.setColumnWidth(1, 110)  # Tipo
        table.setColumnWidth(2, 80)  # Ora
        table.setColumnWidth(3, 200)  # Cliente
        table.setColumnWidth(4, 160)  # Servizio
        table.setColumnWidth(5, 220)  # Dipendenti

    # ---------------- SEGNALI ----------------
    def setup_signals(self):
        self.ui.tableGiorno.clicked.connect(self.open_day_details)
        self.ui.btnGiornoBack.clicked.connect(self.back_to_calendar)


    # ---------------- NAVIGAZIONE ----------------
    def open_day_details(self, qdate: QDate):
        giorno_label = qdate.toString("dd-MM-yyyy")
        self.ui.lblDettaglioTitle.setText(f"Interventi del {giorno_label}")

        # ✅ ricrea la cache e poi carica
        self.build_events_cache_for_month()
        self.load_giorno(qdate)

        self.ui.stackedContent.setCurrentWidget(self.ui.page)

    def back_to_calendar(self):
        self.ui.stackedContent.setCurrentWidget(self.ui.pageCalendario)
        self.refresh_calendar()
    # ---------------- DATI ----------------
    def load_giorno(self, qdate: QDate):
        table = self.ui.tableWidget

        # ✅ prende SINGOLI + RICORRENTI dalla cache
        eventi = self.events_by_date.get(qdate, [])

        table.setRowCount(len(eventi))

        for r, e in enumerate(eventi):
            values = [
                e.get("id_ref", ""),
                e.get("tipo", ""),
                e.get("ora", ""),
                e.get("cliente", ""),
                e.get("servizio", ""),
                e.get("dipendenti", ""),
                e.get("durata", ""),
                e.get("stato", "")
            ]

            for c, v in enumerate(values):
                item = QTableWidgetItem("" if v is None else str(v))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                table.setItem(r, c, item)

        table.clearSelection()



