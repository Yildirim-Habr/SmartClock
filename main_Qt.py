import sys
import os
import time
import pandas as pd
from datetime import datetime
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QStackedWidget, QHBoxLayout
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as patches


class StopwatchScreen(QWidget):
    def __init__(self, app_ref):
        super().__init__()
        self.app_ref = app_ref

        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignCenter)

        self.title = QLabel("Start Now..!!")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setFont(QFont("Arial", 22, QFont.Bold))

        self.time_label = QLabel("00:00:00")
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setFont(QFont("Arial", 32, QFont.Bold))
        self.time_label.setStyleSheet("""
            border: 2px solid grey;
            border-radius: 10px;
            padding: 5px;
        """)

        btn_layout = QHBoxLayout()

        self.start_btn = QPushButton("▶ Start")
        self.start_btn.setFixedSize(100, 50)
        self.start_btn.setStyleSheet("background-color: #4CAF50; color: white; border-radius: 10px;")
        self.start_btn.clicked.connect(self.app_ref.toggle_start)

        self.reset_btn = QPushButton("💾 Save")
        self.reset_btn.setFixedSize(100, 50)
        self.reset_btn.setStyleSheet("background-color: #2196F3; color: white; border-radius: 10px;")
        self.reset_btn.clicked.connect(self.app_ref.reset)

        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.reset_btn)
        
        layout.addWidget(self.title)
        layout.addWidget(self.time_label)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

        self.to_recap_btn = QPushButton(">>", self)
        self.to_recap_btn.move(400 - 50 - 10, 300 - 40 - 10) 
        self.to_recap_btn.setFixedSize(50, 40)
        self.to_recap_btn.setStyleSheet("background-color: black; color: white; border-radius: 10px;")
        self.to_recap_btn.clicked.connect(lambda: self.app_ref.change_screen(1))


class RecapScreen(QWidget):
    def __init__(self, app_ref):
        super().__init__()
        self.app_ref = app_ref

        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignTop)

        self.total_today_label = QLabel("Total Today: 0 hr")
        self.total_today_label.setAlignment(Qt.AlignCenter)
        self.total_today_label.setFont(QFont("Arial", 14, QFont.Bold))

        self.canvas = FigureCanvas(plt.Figure(figsize=(6, 3)))

        self.back_btn = QPushButton("<<")
        self.back_btn.setFixedSize(40, 40)
        self.back_btn.setStyleSheet("background-color: black; color: white; border-radius: 10px;")
        self.back_btn.clicked.connect(lambda: self.app_ref.change_screen(0))

        layout.addWidget(self.total_today_label)
        layout.addWidget(self.canvas)
        layout.addWidget(self.back_btn, alignment=Qt.AlignLeft)

        self.setLayout(layout)

class SmartClockApp(QApplication):
    def resource_path(self, relative_path):
        """Get absolute path to resource, works for dev and for PyInstaller."""
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, relative_path)
    
    def __init__(self, argv):
        super().__init__(argv)

        self.aboutToQuit.connect(self.handle_app_exit)  # Will run when app is closing

        self.running = False
        self.start_time = None
        self.elapsed_time = 0

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)

        self.stack = QStackedWidget()

        self.stopwatch_screen = StopwatchScreen(self)
        self.recap_screen = RecapScreen(self)

        self.stack.addWidget(self.stopwatch_screen)
        self.stack.addWidget(self.recap_screen)

        self.stack.setFixedSize(400, 300)
        self.stack.show()

    def handle_app_exit(self):
        total = self.elapsed_time
        if self.running: 
            total += time.time() - self.start_time

        self.simpan_durasi(total)

    def toggle_start(self):
        if self.running:
            self.timer.stop()
            self.elapsed_time += time.time() - self.start_time
            self.stopwatch_screen.start_btn.setText("▶ Start")
            self.stopwatch_screen.start_btn.setStyleSheet("background-color: #4CAF50; color: white; border-radius: 10px;")
            self.stopwatch_screen.title.setText("Start Now..!!")
        else:
            self.start_time = time.time()
            self.timer.start(100)
            self.stopwatch_screen.start_btn.setText("⏸ Pause")
            self.stopwatch_screen.start_btn.setStyleSheet("background-color: #F44336; color: white; border-radius: 10px;")
            self.stopwatch_screen.title.setText("Fight..!!")
        self.running = not self.running

    def reset(self):
        total = self.elapsed_time if self.start_time else 0
        self.simpan_durasi(total)
        self.elapsed_time = 0
        self.running = False
        self.timer.stop()
        self.stopwatch_screen.time_label.setText("00:00:00")
        self.stopwatch_screen.start_btn.setText("▶ Start")
        self.stopwatch_screen.start_btn.setStyleSheet("background-color: #4CAF50; color: white; border-radius: 5px;")
        self.stopwatch_screen.title.setText("Start Now..!!")

    def simpan_durasi(self, total_detik):
        today = datetime.today().strftime('%Y-%m-%d')
        filename = "data.csv"

        if os.path.exists(filename):
            df = pd.read_csv(filename)
            if today in df['date'].values:
                df.loc[df['date'] == today, 'duration_sec'] += int(total_detik)
            else:
                df.loc[len(df)] = [today, int(total_detik)]
        else:
            df = pd.DataFrame([[today, int(total_detik)]], columns=["date", "duration_sec"])

        df.to_csv(filename, index=False)

    def update_time(self):
        total = time.time() - self.start_time + self.elapsed_time
        self.stopwatch_screen.time_label.setText(time.strftime('%H:%M:%S', time.gmtime(total)))

    def change_screen(self, index):
        self.stack.setCurrentIndex(index)
        if index == 1:
            self.tampilkan_grafik()

    def correcting_days(self, df):
        """Fill missing dates between last date and today with 0 duration"""

        # Ensure we have datetime type
        df['date'] = pd.to_datetime(df['date'])

        # Get date range from last date to today
        last_date = df['date'].max()
        today = pd.to_datetime(datetime.today().date())
        
        if last_date >= today:
            # No correction needed
            return df

        # Create date range only from last date + 1 day to today
        new_dates = pd.date_range(start=last_date + pd.Timedelta(days=1),
                                end=today, freq='D')

        # Create a DataFrame for missing dates
        missing_df = pd.DataFrame({
            'date': new_dates,
            'duration_sec': [0] * len(new_dates)
        })

        # Append and keep order
        df = pd.concat([df, missing_df], ignore_index=True)
        df = df.sort_values('date').reset_index(drop=True)

        # Save corrected data
        df[['date', 'duration_sec']].to_csv("data.csv", index=False)

        return df

    def tampilkan_grafik(self):
        filename = "data.csv"
        if not os.path.exists(filename):
            return
        df = pd.read_csv(filename)
        df['date'] = pd.to_datetime(df['date'])

        df = self.correcting_days(df)

        df['duration_hr'] = df['duration_sec'] / 3600

        fig = self.recap_screen.canvas.figure
        ax = fig.add_subplot(111)  # Create a single set of axes
        
        fig.patches.append(
            patches.Rectangle(
                (0, 0), 1, 1,                # bottom-left corner, width=1, height=1
                transform=fig.transFigure,   # figure-relative coordinates
                fill=False,                   # no fill, just border
                linewidth=2,                  # border thickness
                edgecolor='black'             # border color
            )
        )

        ax.plot(df['date'], df['duration_hr'], marker='o', linewidth=1, markersize=3,
                 color='#4A90E2', markerfacecolor="#4A90E2", markeredgewidth=2)
        ax.fill_between(df['date'], df['duration_hr'], alpha=0.2, color='#4A90E2')
   
        ax.set_title("Activity Duration")
        ax.set_ylabel("Hours")
        # ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
        ax.xaxis.set_visible(False)
        ax.grid(True, alpha=0.3)
        fig.tight_layout()

        self.recap_screen.canvas.draw()

        today = datetime.today().strftime('%Y-%m-%d')
        today_data = df[df['date'] == today]
        total_detik = today_data['duration_sec'].sum() if not today_data.empty else 0
        jam = int(total_detik) // 3600
        menit = int(total_detik % 3600) // 60
        detik = int(total_detik % 60)
        self.recap_screen.total_today_label.setText(f"Total Today: {jam} hr {menit} min {detik} sec")


if __name__ == "__main__":
    app = SmartClockApp(sys.argv)

    icon_path = app.resource_path("icon.ico")

    app.setApplicationName("SmartClock")
    app.setWindowIcon(QIcon(icon_path))  # <-- add here

    app.stack.setWindowTitle("SmartClock")
    app.stack.setWindowIcon(QIcon(icon_path))

    sys.exit(app.exec())
