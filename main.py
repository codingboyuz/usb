import wmi
w = wmi.WMI()
for d in w.Win32_PnPEntity():
    print(d.PNPClass)
    if d.PNPClass == "WPD":
        print(d.Caption, d.PNPDeviceID)
