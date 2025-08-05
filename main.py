from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.core.window import Window
import time
from datetime import datetime
import csv
import os
import pandas as pd
import matplotlib.pyplot as plt
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from kivy.uix.image import Image
from io import BytesIO
import base64

class SmartClockApp(MDApp):
    Window.size = (400, 300)

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Indigo"
        return Builder.load_file("design.kv")

    def on_start(self):
        self.running = False
        self.start_time = None
        self.elapsed_time = 0

    def toggle_start(self):
        screen = self.root.get_screen("stopwatch")
        if self.running: # di 'off' kan
            Clock.unschedule(self.update_time)
            self.elapsed_time += time.time() - self.start_time
            screen.ids.start_btn.icon = "play"
            screen.ids.title.text = "Start Now..!!"
        else: # di 'on' kan
            self.start_time = time.time()
            Clock.schedule_interval(self.update_time, 0.1)
            screen.ids.start_btn.icon = "pause"
            screen.ids.title.text = "Fight..!!"
        self.running = not self.running

    def reset(self):
        screen = self.root.get_screen("stopwatch")
        Clock.unschedule(self.update_time)
        total = self.elapsed_time if self.start_time else 0
        self.simpan_durasi(total)
        self.elapsed_time = 0
        self.running = False
        screen.ids.time_label.text = "00:00:00"
        screen.ids.start_btn.icon = "play"
        screen.ids.title.text = "Start Now..!!"

    def simpan_durasi(self, total_detik):
        today = datetime.today().strftime('%Y-%m-%d')
        filename = "belajar.csv"

        if os.path.exists(filename):
            df = pd.read_csv(filename)
            if today in df['tanggal'].values:
                index = df[df['tanggal'] == today].index[0]
                df.at[index, 'durasi_detik'] = int(df.at[index, 'durasi_detik']) + int(total_detik)
            else:
                df.loc[len(df.index)] = [today, int(total_detik)]
        else:
            df = pd.DataFrame([[today, int(total_detik)]], columns=["tanggal", "durasi_detik"])

        df.to_csv(filename, index=False)

    def update_time(self, dt):
        screen = self.root.get_screen("stopwatch")
        total = time.time() - self.start_time + self.elapsed_time
        screen.ids.time_label.text = time.strftime('%H:%M:%S', time.gmtime(total))

    def change_screen(self, screen_name):
        self.root.current = screen_name
        if screen_name == "recap":
            self.tampilkan_grafik()

    def tampilkan_grafik(self):
        screen = self.root.get_screen("recap")
        box = screen.ids.grafik_box
        box.clear_widgets()

        if not os.path.exists("belajar.csv"):
            return

        df = pd.read_csv("belajar.csv")
        df['tanggal'] = pd.to_datetime(df['tanggal'])
        df['durasi_jam'] = df['durasi_detik'] / 3600

        fig, ax = plt.subplots()
        ax.plot(df['tanggal'], df['durasi_jam'], marker='o')
        ax.set_title("Durasi Belajar per Hari")
        ax.set_ylabel("Jam")
        ax.set_xlabel("Tanggal")
        fig.autofmt_xdate()
        fig.tight_layout()

        # Render plot ke gambar PNG
        buffer = BytesIO()
        fig.savefig(buffer, format='png')
        buffer.seek(0)
        image_data = base64.b64encode(buffer.read()).decode('utf-8')
        buffer.close()

        # Tampilkan gambar di dalam BoxLayout
        img = Image()
        img.texture = Image(source=f'data:image/png;base64,{image_data}').texture
        box.add_widget(img)

        # Update label total hari ini dalam format jam, menit, detik
        today = pd.to_datetime(datetime.today().strftime('%Y-%m-%d'))
        today_data = df[df['tanggal'] == today]
        total_detik = today_data['durasi_detik'].sum() if not today_data.empty else 0
        jam = int(total_detik) // 3600
        menit = int(total_detik % 3600) // 60
        detik = int(total_detik % 60)
        screen.ids.total_today_label.text = f"Total Hari Ini: {jam} jam {menit} menit {detik} detik"

if __name__ == "__main__":
    SmartClockApp().run()
