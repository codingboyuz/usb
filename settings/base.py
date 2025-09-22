import os
from  pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Database path
DB_FILE = BASE_DIR / 'data' / "sql.db"
INSTALLER_DIR = BASE_DIR / "apps" / "installer" / "binaries"
EXE_USB_EJECT = INSTALLER_DIR / "untitled2.exe"
EXE_MTP_EJECT = INSTALLER_DIR / "untitled3.exe"
