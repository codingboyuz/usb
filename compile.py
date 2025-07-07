# compile.py
import PyInstaller.__main__

PyInstaller.__main__.run([
    'core/usb_watcher.py',
    '--onefile',
    '--windowed',
    '--noconsole',
    '--add-data', 'db/database.py;db',
    '--add-data', 'core/usb_eject.py;core',
    '--name', 'usb_killer',
    '--distpath', 'installer'
])