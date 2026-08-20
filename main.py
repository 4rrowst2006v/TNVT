from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
import socket
import threading
import json
from concurrent.futures import ThreadPoolExecutor

class ScannerApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        self.btn = Button(
            text="CHẠY QUÉT (QUET.PY CORE)", 
            size_hint_y=None, 
            height=80,
            background_color=(0.1, 0.6, 0.8, 1)
        )
        self.btn.bind(on_press=self.start_scan)
        
        self.result_label = Label(
            text="Chờ lệnh quét từ quet.py...", 
            size_hint_y=None, 
            halign='left', 
            valign='top'
        )
        self.result_label.bind(texture_size=self.result_label.setter('size'))
        
        self.scroll = ScrollView()
        self.scroll.add_widget(self.result_label)
        
        self.layout.add_widget(self.btn)
        self.layout.add_widget(self.scroll)
        return self.layout

    def start_scan(self, instance):
        self.btn.disabled = True
        self.result_label.text = "Đang quét mạng theo logic quet.py..."
        threading.Thread(target=self.run_quet_logic).start()

    def run_quet_logic(self):
        # Tự động lấy dải subnet hiện tại
        subnet = "192.168.1"
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(1)
            s.connect(("10.255.255.255", 1))
            local_ip = s.getsockname()[0]
            s.close()
            subnet = ".".join(local_ip.split(".")[:3])
        except Exception:
            pass

        found_devices = []

        def check_device(ip):
            target_ip = f"{subnet}.{ip}"
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.3)
                if s.connect_ex((target_ip, 5555)) == 0:
                    # Trả về thông tin cấu trúc JSON chuẩn của quet.py
                    device_data = {
                        "ip": target_ip,
                        "port": 5555,
                        "status": "online"
                    }
                    found_devices.append(device_data)
                s.close()
            except Exception:
                pass

        # Đa luồng quét siêu tốc
        with ThreadPoolExecutor(max_workers=128) as executor:
            executor.map(check_device, range(1, 255))

        # Xuất dữ liệu JSON
        output_json = json.dumps(found_devices, indent=4, ensure_ascii=False)
        Clock.schedule_once(lambda dt: self.update_ui(output_json, len(found_devices)))

    def update_ui(self, json_text, count):
        self.btn.disabled = False
        if count > 0:
            self.result_label.text = f"Tìm thấy {count} thiết bị (JSON):\n\n" + json_text
        else:
            self.result_label.text = "Không tìm thấy thiết bị nào mở cổng 5555!"

if __name__ == '__main__':
    ScannerApp().run()
