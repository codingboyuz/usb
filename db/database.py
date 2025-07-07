import sqlite3
from datetime import datetime

DB_FILE = '../sql.db'

# Codeni chatGPt yozgan

class LocalDatabase:
    def __init__(self):
        self.connection = sqlite3.connect(DB_FILE)
        self.init_db()

    def init_db(self):
        with self.connection:
            self.connection.execute('''
            CREATE TABLE IF NOT EXISTS registered_devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                serial TEXT UNIQUE NOT NULL 
            )''')

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
                    "INSERT INTO usb_access_log (timestamp, caption, model,interface_type,size,serial) VALUES (?,?,?,?,?,?)",
                    (datetime.now().isoformat(), caption, model, interface_type, size, serial))
                print(f"✅ Log yozildi: {caption}")
        except sqlite3.Error as e:
            print(f"Database error in log_access: {e}")

    def close_connection(self):
        if self.connection:
            self.connection.close()
            self.connection = None
