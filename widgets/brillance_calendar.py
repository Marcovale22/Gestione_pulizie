from PyQt6.QtWidgets import QCalendarWidget
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtCore import QPoint

class BrillanceCalendar(QCalendarWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._events_by_date = {}

    def setEvents(self, events_by_date: dict):
        self._events_by_date = events_by_date or {}
        self.update()

    def paintCell(self, painter: QPainter, rect, date):
        # ✅ prima disegna la cella normale (numero incluso)
        super().paintCell(painter, rect, date)

        evs = self._events_by_date.get(date, [])
        if not evs:
            return

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        r = 4
        cx = rect.center().x()
        cy = rect.bottom() - 9  # un pelo più su

        painter.setBrush(QColor("#2563EB"))
        painter.setPen(QColor("#2563EB"))
        painter.drawEllipse(QPoint(cx, cy), r, r)

        painter.restore()
