import subprocess


EXE_FILE = 'usb_eject.exe'

def eject_usb(pnp_id):
    try:
        result = subprocess.run(
            [EXE_FILE, pnp_id],  # PNPDeviceID argument sifatida uzatiladi
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print(result.stdout)
        if result.stderr:
            print(f"[Eject xatosi] {result.stderr}")
    except Exception as e:
        print(f"[Subprocess xatosi] {e}")

eject_usb(r'USBSTOR\DISK&VEN_VENDORCO&PROD_PRODUCTCODE&REV_2.00\7956101095918431346&0')