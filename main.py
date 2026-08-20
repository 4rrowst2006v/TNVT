from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
import socket
import threading
from concurrent.futures import ThreadPoolExecutor

class RemoteADBMasterApp(App):
    def build(self):
        # Thiết lập giao diện nền tối tổng thể
        self.root_layout = BoxLayout(orientation='vertical', padding=15, spacing=15)
        with self.root_layout.canvas.before:
            Color(0.07, 0.07, 0.07, 1) # Màu nền đen xám đậm
            self.bg_rect = Rectangle(size=self.root_layout.size, pos=self.root_layout.pos)
        self.root_layout.bind(size=self._update_bg, pos=self._update_bg)

        # --- TIÊU ĐỀ TRÊN CÙNG ---
        title_layout = BoxLayout(size_hint_y=None, height=40)
        title_label = Label(
            text="Remote ADB [color=#2ecc71]Master[/color]", 
            font_size=20, 
            bold=True, 
            markup=True, 
            halign='left', 
            valign='middle'
        )
        title_label.bind(size=title_label.setter('text_size'))
        
        version_label = Label(
            text="v2.4", 
            font_size=12, 
            color=(0.6, 0.6, 0.6, 1), 
            size_hint_x=None, 
            width=40,
            halign='right',
            valign='middle'
        )
        version_label.bind(size=version_label.setter('text_size'))
        
        title_layout.add_widget(title_label)
        title_layout.add_widget(version_label)
        self.root_layout.add_widget(title_layout)

        # --- DANH SÁCH THIẾT BỊ (QUÉT TỰ ĐỘNG) ---
        sec1_layout = BoxLayout(size_hint_y=None, height=30, spacing=10)
        sec1_label = Label(
            text="DANH SÁCH THIẾT BỊ (QUÉT TỰ ĐỘNG)", 
            font_size=11, 
            color=(0.6, 0.6, 0.6, 1), 
            halign='left',
            valign='middle'
        )
        sec1_label.bind(size=sec1_label.setter('text_size'))
        
        btn_rescan = Button(
            text="Quét lại", 
            font_size=12, 
            size_hint_x=None, 
            width=70, 
            background_color=(0.1, 0.4, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        btn_rescan.bind(on_press=self.start_scan)
        
        sec1_layout.add_widget(sec1_label)
        sec1_layout.add_widget(btn_rescan)
        self.root_layout.add_widget(sec1_layout)

        # Khung chứa thiết bị quét được (Giống hộp thoại trong mẫu)
        self.device_scroll = ScrollView(size_hint_y=None, height=130)
        self.device_list_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=5)
        self.device_list_layout.bind(minimum_height=self.device_list_layout.setter('height'))
        
        self.status_label = Label(
            text="Đang quét mạng tìm thiết bị ADB...", 
            font_size=14, 
            color=(0.8, 0.8, 0.8, 1),
            halign='center',
            valign='middle'
        )
        self.status_label.bind(size=self.status_label.setter('text_size'))
        self.device_list_layout.add_widget(self.status_label)
        self.device_scroll.add_widget(self.device_list_layout)
        self.root_layout.add_widget(self.device_scroll)

        # --- THAO TÁC TRÊN MÁY ĐÃ CHỌN ---
        sec2_label = Label(
            text="THAO TÁC TRÊN MÁY ĐÃ CHỌN", 
            font_size=11, 
            color=(0.6, 0.6, 0.6, 1), 
            size_hint_y=None, 
            height=25, 
            halign='left',
            valign='middle'
        )
        sec2_label.bind(size=sec2_label.setter('text_size'))
        self.root_layout.add_widget(sec2_label)

        # Các nút chức năng tạm thời vô hiệu hóa theo yêu cầu
        actions_layout = BoxLayout(orientation='vertical', spacing=10)
        
        self.btn_screen = Button(text="⚡ Tắt / Mở Màn hình", disabled=True, background_color=(0.18, 0.18, 0.18, 1), color=(0.5, 0.5, 0.5, 1))
        self.btn_capture = Button(text="Chụp màn hình máy đích", disabled=True, background_color=(0.18, 0.18, 0.18, 1), color=(0.5, 0.5, 0.5, 1))
        self.btn_battery = Button(text="Xem chi tiết Pin", disabled=True, background_color=(0.18, 0.18, 0.18, 1), color=(0.5, 0.5, 0.5, 1))
        self.btn_reboot = Button(text="Reboot máy đích", disabled=True, background_color=(0.18, 0.18, 0.18, 1), color=(0.7, 0.3, 0.3, 1))

        actions_layout.add_widget(self.btn_screen)
        actions_layout.add_widget(self.btn_capture)
        actions_layout.add_widget(self.btn_battery)
        actions_layout.add_widget(self.btn_reboot)
        
        self.root_layout.add_widget(actions_layout)

        # Tự động chạy quét ngay khi mở app
        Clock.schedule_once(self.start_scan, 0.5)

        return self.root_layout

    def _update_bg(self, instance, value):
        self.bg_rect.size = instance.size
        self.bg_rect.pos = instance.pos

    def start_scan(self, instance=None):
        self.status_label.text = "Đang quét mạng tìm thiết bị ADB..."
        self.device_list_layout.clear_widgets()
        self.device_list_layout.add_widget(self.status_label)
        threading.Thread(target=self.run_scan_core).start()

    def run_scan_core(self):
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

        found = []
        def check(ip):
            target_ip = f"{subnet}.{ip}"
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.3)
                if s.connect_ex((target_ip, 5555)) == 0:
                    found.append(target_ip)
                s.close()
            except: pass

        with ThreadPoolExecutor(max_workers=128) as executor:
            executor.map(check, range(1, 255))

        Clock.schedule_once(lambda dt: self.update_device_ui(found))

    def update_device_ui(self, devices):
        self.device_list_layout.clear_widgets()
        if devices:
            for ip in devices:
                btn_dev = Button(
                    text=f"📱 Thiết bị: {ip}:5555",
                    size_hint_y=None,
                    height=45,
                    background_color=(0.12, 0.3, 0.18, 1),
                    color=(1, 1, 1, 1)
                )
                self.device_list_layout.add_widget(btn_dev)
        else:
            lbl = Label(
                text="Không tìm thấy thiết bị ADB nào!", 
                color=(0.8, 0.3, 0.3, 1), 
                size_hint_y=None, 
                height=40
            )
            self.device_list_layout.add_widget(lbl)

if __name__ == '__main__':
    RemoteADBMasterApp().run()
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
