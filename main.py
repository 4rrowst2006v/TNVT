from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
import socket
import threading
from concurrent.futures import ThreadPoolExecutor

class ScannerApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.btn = Button(text="QUÉT MẠNG TÌM CỔNG 5555", size_hint_y=None, height=100)
        self.btn.bind(on_press=self.start_scan)
        self.result_label = Label(text="Chờ lệnh quét...", size_hint_y=None, halign='left', valign='top')
        self.result_label.bind(texture_size=self.result_label.setter('size'))
        self.scroll = ScrollView()
        self.scroll.add_widget(self.result_label)
        self.layout.add_widget(self.btn)
        self.layout.add_widget(self.scroll)
        return self.layout

    def start_scan(self, instance):
        self.btn.disabled = True
        self.result_label.text = "Đang quét dải 192.168.1.1 - 254..."
        threading.Thread(target=self.do_scan).start()

    def do_scan(self):
        found = []
        def check(ip):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.3)
                if s.connect_ex((ip, 5555)) == 0:
                    found.append(ip)
                s.close()
            except: pass
        
        with ThreadPoolExecutor(max_workers=50) as executor:
            executor.map(check, [f"192.168.1.{i}" for i in range(1, 255)])
        
        Clock.schedule_once(lambda dt: self.show_result(found))

    def show_result(self, found):
        self.btn.disabled = False
        if found:
            self.result_label.text = "Tìm thấy:\n" + "\n".join([f"-> {ip}:5555" for ip in found])
        else:
            self.result_label.text = "Không tìm thấy thiết bị nào!"

if __name__ == '__main__':
    ScannerApp().run()
