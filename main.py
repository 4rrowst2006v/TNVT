from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
import socket
from concurrent.futures import ThreadPoolExecutor

class ScannerApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical')
        self.result_label = Label(text="Chưa quét")
        self.btn = Button(text="Quét mạng 5555", on_press=self.start_scan)
        self.layout.add_widget(self.result_label)
        self.layout.add_widget(self.btn)
        return self.layout

    def start_scan(self, instance):
        self.result_label.text = "Đang quét..."
        # Gọi logic quét ở đây (dùng lại cái hàm check_port_and_ping đã chốt)
        Clock.schedule_once(self.run_scan_thread, 0.1)

    def run_scan_thread(self, dt):
        # Tích hợp logic quét socket vào đây
        # ... (Dán logic socket từ script cũ của mình vào)
        self.result_label.text = "Đã quét xong (tạm thời chưa có dữ liệu)"

if __name__ == '__main__':
    ScannerApp().run()
    