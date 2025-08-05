from kivy.config import Config
Config.set('graphics', 'resizable', '0')
Config.set('graphics', 'width', '400')
Config.set('graphics', 'height', '300')

from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.clock import Clock
import time
from datetime import datetime
import csv
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from kivy.uix.image import Image
from io import BytesIO
import base64

class SmartClockApp(MDApp):

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
        filename = "data.csv"

        if os.path.exists(filename):
            df = pd.read_csv(filename)
            if today in df['date'].values:
                index = df[df['date'] == today].index[0]
                df.at[index, 'duration_sec'] = int(df.at[index, 'duration_sec']) + int(total_detik)
            else:
                df.loc[len(df.index)] = [today, int(total_detik)]
        else:
            df = pd.DataFrame([[today, int(total_detik)]], columns=["date", "duration_sec"])

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

        if not os.path.exists("data.csv"):
            return

        # make the plot
        df = pd.read_csv("data.csv")
        df['date'] = pd.to_datetime(df['date'])
        df['duration_hr'] = df['duration_sec'] / 3600

        # Create beautiful plot
        plt.figure(figsize=(12, 6))
        plt.plot(df['date'], df['duration_sec'], 
                marker='o', linewidth=3, markersize=8,
                color='#4A90E2', markerfacecolor='#F5A623',
                markeredgecolor='white', markeredgewidth=2)

        # Fill area under curve
        plt.fill_between(df['date'], df['duration_hr'], 
                        alpha=0.2, color='#4A90E2')

        # Beautiful styling
        plt.title('Activity Duration', fontsize=18, fontweight='bold', pad=20)
        plt.ylabel('Hour', fontsize=14)
        plt.xlabel('Date', fontsize=14)
        plt.ylim(0, None)

        # Format dates
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
        plt.xticks(rotation=45)

        # Clean grid
        plt.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
        plt.gca().set_facecolor('#FAFAFA')

        # Perfect layout
        plt.tight_layout()

        # Get current figure
        fig = plt.gcf()

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
        today_data = df[df['date'] == today]
        total_detik = today_data['duration_sec'].sum() if not today_data.empty else 0
        jam = int(total_detik) // 3600
        menit = int(total_detik % 3600) // 60
        detik = int(total_detik % 60)
        screen.ids.total_today_label.text = f"Total Today: {jam} hr {menit} min {detik} sec"

if __name__ == "__main__":
    SmartClockApp().run()
