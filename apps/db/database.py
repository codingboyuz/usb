import sqlite3
from datetime import datetime
from settings.base import DB_FILE


class LocalDatabase:
    def __init__(self):
        # check_same_thread=False → ko‘p threadlar bilan ishlash uchun
        self.connection = sqlite3.connect(DB_FILE, check_same_thread=False)
        self.init_db()

    def init_db(self):
        with self.connection:
            # USB qurilmalar ro‘yxati
            self.connection.execute('''
            CREATE TABLE IF NOT EXISTS registered_devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                serial TEXT UNIQUE NOT NULL
            )''')

            # USB ulanish loglari
            self.connection.execute('''
            CREATE TABLE IF NOT EXISTS usb_access_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                caption TEXT,
                model TEXT,
                interface_type TEXT,
                size TEXT,
                serial TEXT
            )''')

            # ✅ Admin foydalanuvchilari jadvali
            self.connection.execute('''
            CREATE TABLE IF NOT EXISTS admin_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )''')

            # Default admin foydalanuvchisini qo‘shish (agar bo‘lmasa)
            cur = self.connection.cursor()
            cur.execute("SELECT 1 FROM admin_users WHERE username = ?", ("admin",))
            if not cur.fetchone():
                cur.execute(
                    "INSERT INTO admin_users (username, password) VALUES (?, ?)",
                    ("admin", "123456")
                )
                print("✅ Default admin foydalanuvchi yaratildi (username='admin', password='123456')")

    # ---- USB bilan ishlovchi metodlar ----
    def is_serial_registered(self, serial):
        try:
            with self.connection:
                cursor = self.connection.cursor()
                cursor.execute("SELECT 1 FROM registered_devices WHERE serial = ?", (serial,))
                return cursor.fetchone() is not None
        except sqlite3.Error as e:
            print(f"Database error in is_serial_registered: {e}")
            return False

    def add_device(self, serial: str):
        try:
            with self.connection:
                self.connection.execute(
                    "INSERT INTO registered_devices (serial) VALUES (?)",
                    (serial,))
        except sqlite3.Error as e:
            print(f"Database error in registered_devices: {e}")

    def log_access(self, caption: str, model: str, interface_type: str, size: str, serial: str):
        try:
            with self.connection:
                self.connection.execute(
                    "INSERT INTO usb_access_log "
                    "(timestamp, caption, model, interface_type, size, serial) "
                    "VALUES (?,?,?,?,?,?)",
                    (datetime.now().isoformat(), caption, model, interface_type, size, serial)
                )
                print(f"✅ Log yozildi: {caption}")
        except sqlite3.Error as e:
            print(f"Database error in log_access: {e}")

    # ---- Admin foydalanuvchilar bilan ishlovchi oddiy metodlar ----
    def verify_admin(self, username: str, password: str) -> bool:
        """
        Admin loginini tekshiradi.
        """
        with self.connection:
            cur = self.connection.cursor()
            cur.execute(
                "SELECT 1 FROM admin_users WHERE username=? AND password=?",
                (username, password)
            )
            return cur.fetchone() is not None

    def close_connection(self):
        if self.connection:
            self.connection.close()
            self.connection = None
