from kivy.config import Config
Config.set('kivy', 'window_icon', 'icon.ico')
Config.set('graphics', 'resizable', '0')
Config.set('graphics', 'width', '400')
Config.set('graphics', 'height', '300')

from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivy.uix.screenmanager import SlideTransition
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDFloatingActionButton
from kivy.uix.screenmanager import ScreenManager
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from io import BytesIO
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import time
import os
import base64
import sys
import pandas as pd

class StopwatchScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = MDLabel(text="Start Now..!!", halign="center", font_style="H5",
                             theme_text_color="Custom", text_color=(1, 1, 1, 1),
                             pos_hint={"center_x": 0.5, "center_y": 0.8})

        self.time_label = MDLabel(text="00:00:00", halign="center", font_style="H2",
                                  theme_text_color="Custom", text_color=(1, 1, 1, 1),
                                  pos_hint={"center_x": 0.5, "center_y": 0.55})

        self.start_btn = MDFloatingActionButton(icon="play", md_bg_color=(0.2, 0.6, 1, 1),
                                                size_hint=(0.17, 0.2),
                                                pos_hint={"center_x": 0.4, "center_y": 0.25},
                                                on_release=lambda x: MDApp.get_running_app().toggle_start())

        self.reset_btn = MDFloatingActionButton(icon="content-save", md_bg_color=(1, 0.3, 0.3, 1),
                                                size_hint=(0.17, 0.2),
                                                pos_hint={"center_x": 0.6, "center_y": 0.25},
                                                on_release=lambda x: MDApp.get_running_app().reset())

        self.to_recap_btn = MDFloatingActionButton(icon="arrow-right", md_bg_color="black",
                                                   size_hint=(0.17, 0.2),
                                                   pos_hint={"center_x": 0.92, "center_y": 0.1},
                                                   on_release=lambda x: MDApp.get_running_app().change_screen("recap",  'left'))

        self.add_widget(self.title)
        self.add_widget(self.time_label)
        self.add_widget(self.start_btn)
        self.add_widget(self.reset_btn)
        self.add_widget(self.to_recap_btn)

class RecapScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')

        self.total_today_label = MDLabel(text="Total Hari Ini: 0 jam", halign="center",
                                         font_style="H6", size_hint_y=0.2,
                                         theme_text_color="Custom", text_color=(1, 1, 1, 1))

        self.grafik_box = BoxLayout(orientation='vertical', size_hint=(0.9, 0.8),
                                    pos_hint={'center_x': 0.5, 'center_y': 0.5})

        self.back_btn = MDFloatingActionButton(icon="arrow-left", md_bg_color="black",
                                               size_hint=(0.17, 0.2),
                                               pos_hint={"center_x": 0.1, "center_y": 0.1},
                                               on_release=lambda x: MDApp.get_running_app().change_screen("stopwatch",  'right'))

        self.layout.add_widget(self.total_today_label)
        self.layout.add_widget(self.grafik_box)
        self.layout.add_widget(self.back_btn)
        self.add_widget(self.layout)

class SmartClockApp(MDApp):
    def resource_path(self, relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Indigo"
        self.screen_manager = ScreenManager()
        self.stopwatch_screen = StopwatchScreen(name="stopwatch")
        self.recap_screen = RecapScreen(name="recap")
        self.screen_manager.add_widget(self.stopwatch_screen)
        self.screen_manager.add_widget(self.recap_screen)
        return self.screen_manager

    def on_start(self):
        self.running = False
        self.start_time = None
        self.elapsed_time = 0

    def toggle_start(self):
        screen = self.stopwatch_screen
        time_now = time.time()
        if self.running:
            Clock.unschedule(self.update_time)
            self.elapsed_time += time_now - self.start_time
            screen.start_btn.icon = "play"
            screen.title.text = "Start Now..!!"
        else:
            self.start_time = time_now
            Clock.schedule_interval(self.update_time, 0.1)
            screen.start_btn.icon = "pause"
            screen.title.text = "Fight..!!"
        self.running = not self.running

    def reset(self):
        screen = self.stopwatch_screen
        Clock.unschedule(self.update_time)
        total = self.elapsed_time if self.start_time else 0
        self.simpan_durasi(total)
        self.elapsed_time = 0
        self.running = False
        screen.time_label.text = "00:00:00"
        screen.start_btn.icon = "play"
        screen.title.text = "Start Now..!!"

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
        screen = self.stopwatch_screen
        total = time.time() - self.start_time + self.elapsed_time
        screen.time_label.text = time.strftime('%H:%M:%S', time.gmtime(total))

    def on_stop(self):
        # Only save if the stopwatch not already saved
        # if self.running:
        total = self.elapsed_time
        if self.start_time:
            total += time.time() - self.start_time
        if total > 0:  # Only save if there's actually time to save
            self.simpan_durasi(total)
        return super().on_stop()

    def change_screen(self, screen_name, direction):
        self.screen_manager.transition = SlideTransition(direction=direction)
        self.screen_manager.current = screen_name
        if screen_name == "recap":
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
        screen = self.recap_screen
        box = screen.grafik_box
        box.clear_widgets()

        if not os.path.exists("data.csv"):
            return

        df = pd.read_csv("data.csv")
        df['date'] = pd.to_datetime(df['date'])

        df = self.correcting_days(df)
        
        df['duration_hr'] = df['duration_sec'] / 3600

        plt.figure(figsize=(12, 6))
        plt.plot(df['date'], df['duration_hr'], marker='o', linewidth=3, markersize=8,
                 color='#4A90E2', markerfacecolor="#4A90E2",
                 markeredgecolor='white', markeredgewidth=2)

        plt.fill_between(df['date'], df['duration_hr'], alpha=0.2, color='#4A90E2')
        plt.title('Activity Duration', fontsize=18, fontweight='bold', pad=20)
        plt.ylabel('Hour', fontsize=14)
        plt.xlabel('Date', fontsize=14)
        plt.ylim(0, None)
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
        plt.gca().set_facecolor('#FAFAFA')
        plt.tight_layout()

        fig = plt.gcf()
        buffer = BytesIO()
        fig.savefig(buffer, format='png')
        buffer.seek(0)
        image_data = base64.b64encode(buffer.read()).decode('utf-8')
        buffer.close()

        img = Image()
        img.texture = Image(source=f'data:image/png;base64,{image_data}').texture
        box.add_widget(img)

        today = pd.to_datetime(datetime.today().strftime('%Y-%m-%d'))
        today_data = df[df['date'] == today]
        total_detik = today_data['duration_sec'].sum() if not today_data.empty else 0
        jam = int(total_detik) // 3600
        menit = int(total_detik % 3600) // 60
        detik = int(total_detik % 60)
        screen.total_today_label.text = f"Total Today: {jam} hr {menit} min {detik} sec"

if __name__ == "__main__":
    SmartClockApp().run()
