import sys
from PyQt6.QtWidgets import QApplication

from database.database import init_db
from windows.main_window import MainWindow


if __name__ == "__main__":
    # 1) Inizializzo il DB (crea file + tabelle se mancano)
    init_db()

    # 2) Avvio l'app
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())



