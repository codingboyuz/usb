

# 1) Qisqacha arxitektura — kim nimani bajaradi

1. **Host controller (xHCI / EHCI va h.k.)** — fizik portdagi hodisani sezadi, portni reset qiladi, qurilmadan USB deskriptorlari oladi (enumeration). Bu kernelning eng past darajasi. ([Microsoft Learn][1])
2. **Hub driver (`usbhub.sys`)** — hub/portlar uchun mas’ul, yangi funksiyalarni aniqlaydi va PnP menejerga (Plug and Play) xabar beradi. ([Microsoft Learn][1])
3. **PnP manager va Device Node (DevNode)** — PnP qurilma uchun DevNode yaratadi va mos class/function driverlarni yuklaydi (masalan, usbstor, winusb, hidclass). ([Microsoft Learn][1])
4. **Class / Function draiverlar (kernel)** — qurilmaga mos class driver (USBSTOR, HID, WpdBusEnum va h.k.) yuklanadi; agar kerak bo‘lsa KMDF function driver yoziladi. ([Microsoft Learn][1])
5. **User-mode APIlar / stack** — tizimdan xabar olish uchun `WM_DEVICECHANGE`/`RegisterDeviceNotification`, `SetupDi*` (SetupAPI), yoki yuqori darajada WMI eventlar ishlatiladi. Bu daraja ilovalarga hodisani yetkazadi. ([Microsoft Learn][2])

---

# 2) Qaysi qatlam — qaysi maqsad uchun (tezlik va xavfsizlik nuqtai nazari)

* **Agar maqsadingiz — maksimal tezlik va ishonchli xavfsizlik (korporativ policy: bloklash/karantinlash) → KERNEL-MODE (KMDF) filter driver.**

  * Nega? Chunki kernel-mode filter driver (upper filter) USB hub yoki host controller devicening ustiga ulanib, PnP IRP yoki USB requestlarni (IRP_MJ_PNP, IRP_MJ_DEVICE_CONTROL va hk.) o‘rta darajada ushlab, qurilma enumeration jarayonini bloklashi yoki yo‘lini o‘zgartirishi mumkin. Bu eng erta nuqtada (enumeration bosqichida) intervence beradi — shuning uchun “yuqori tezlikda aniqlash” va “bloklash” uchun ma'qul. ([Microsoft Learn][3])
* **Agar maqsad — monitoring va jurnalga yozish, lekin kernel darajasidagi haqiqiy bloklash shart emas → USER-MODE (WMI / WM_DEVICECHANGE + SetupAPI).**

  * Oddiy va xavfsiz; lekin ba’zan (ayniqsa drayver yuklanishi / enumeration jarayonining juda dastlabki bosqichlari) user-mode kechikishi mumkin. WMI bilan 1–2 soniya ichida event olinadi (polling bilan) — lekin kernel filter kabi “stop” qila olmaysiz. ([Microsoft Learn][2])

---

# 3) Konkret texnik variantlar (va qaysi biridan foydalanish tavsiya etiladi)

1. **KMDF Upper Filter Driver on USB Hub (TAVSIYA — korporativ security):**

   * Yozing: KMDF asosida **upper filter** qurib, `IoAttachDeviceToDeviceStackSafe` orqali hub yoki function driver stackiga ulanadi. Shu orqali siz IRPlarni tekshirib, qurilma `IRP_MN_START_DEVICE` bosqichida yoki `IRP_MJ_PNP` so‘rovlarida intervension qila olasiz. Bu usul qurilmalarni **enumeration bosqichida** bloklash yoki identifikatorni (VID/PID) ko‘rib ruxsat/deny qilish imkonini beradi. ([Microsoft Learn][4])
   * Foydalaniladigan APIlar / konseptlar: `IoAttachDeviceToDeviceStackSafe`, `DriverEntry`/`EvtDeviceAdd` (KMDF), IRP handlerlar, INF fayl bilan driver o‘rnatish. Microsoft sample kodlari WDK repoda mavjud. ([Microsoft Learn][5])

2. **Kernel callback registration (IoRegisterPlugPlayNotification):**

   * Agar siz butun tizim bo‘ylab PnP hodisalarini juda tez olishni xohlasangiz, kernel modeda `IoRegisterPlugPlayNotification` bilan PnP event callback ro‘yxatdan o‘tkazish mumkin. Bu real-time xabar beradi va siz darhol devnode haqida ma’lumot olishingiz mumkin. Ammo to‘liq bloklash uchun filter driver kerak bo‘lishi mumkin. ([Microsoft Learn][6])

3. **UMDF (user-mode driver) yoki UMDF v2 filter:**

   * UMDF v2 user-mode driver host processida ishlaydi; ba’zida kernel driverga qaraganda osonroq yoziladi lekin **real-time bloklash qobiliyati kamroq** va ishlash tezligi kerneldan oshmaydi. Security-critical korporativ yechimlar uchun KMDF (kernel) tavsiya qilinadi. ([Microsoft Learn][7])

4. **User-mode monitoring (WMI / WM_DEVICECHANGE / SetupDi):**

   * Tez yoziladi, testlash oson, lekin enumerationning eng birinchi bosqichlarida qurilmani qaytadan bloklay olmaysiz. Agar siz faqat **tezda xabar olmoqchi** bo‘lsangiz, `RegisterDeviceNotification` + `SetupDiGetClassDevs` yoki WMI eventlar yetarli. ([Microsoft Learn][5])

---

# 4) “Eject” va qurilmani olib tashlash qanday amalga oshiriladi

* **Mass-storage eject:** `DeviceIoControl` orqali `IOCTL_STORAGE_EJECT_MEDIA` va SCSI/Stor IOCTLlar yordamida chiqish buyuriladi (user-mode yoki kernel-mode orqali). Biroq bu faqat media ejectionni soʻraydi; agar qurilma butunlay PnP darajasida olib tashlanishi kerak bo‘lsa, `CM_Request_DeviceEject` (Configuration Manager API) yoki kernelda PnP ejection MDL'lari ishlatiladi. ([Microsoft Learn][4])

---

# 5) Amaliy tavsiyalar — sizning korporativ maqsad uchun

1. **Agar korporativ xavfsizlik va “real-time blocking” – yozing KMDF upper filter driver** va uni USB hub PDO ustiga o‘rnatish. Bu eng erta nuqtada qurilmani aniqlash va bloklash imkonini beradi. (Ammo driver signing, INF va test muhitiga eʼtibor bering — unsigned driver Windows 10/11 da ishlamaydi unless test mode yoki driver signed). ([Microsoft Learn][3])
2. **Qo‘shimcha: user-mode monitoring agent (WMI/WM_DEVICECHANGE)** — KMDF driver bilan yonma-yon ishlaydigan agent yaratish mumkin: kernel driver bloklaydi yoki tagga qo‘yadi; user-mode agent esa jurnal, policy va alerting qiladi. Bu kombinatsiya ko‘proq amaliy va boshqarilishi oson. ([Microsoft Learn][2])
3. **Driver deploy va signing:** korporativ darajada WDK/WDK build, driver signing (EV cert) va INF orqali o‘rnatish talab etiladi. Windows-ning driver signing siyosati (Secure Boot, signature enforcement) bilan mos bo‘lishi kerak. ([GitHub][8])

---

# 6) Muhim hujjatlar / maqolalar (o‘qib chiqishingiz uchun, eng keraklilari)

* **USB 3.0 driver stack architecture (Windows)** — umumiy arxitektura va draiverlar. ([Microsoft Learn][1])
* **IoRegisterPlugPlayNotification (kernel)** — kernelda PnP eventlar uchun ro‘yxatdan o‘tish. ([Microsoft Learn][6])
* **Sample KMDF drivers (Microsoft samples repo)** — KMDF bilan filter/function driver misollari. ([Microsoft Learn][5])
* **IoAttachDeviceToDeviceStackSafe** — filter driverni device stackga ulash texnikasini tushuntiradi. ([Microsoft Learn][4])
* **Example WDM device stack & filter drivers** — upper/lower filter konseptlari va misollar. ([Microsoft Learn][3])

(Agar xohlasangiz, ushbu sahifalarning toʻliq URL’larini hozir yuboraman va kerakli joylarni belgilab chiqib, sizga mos KMDF skeleton kodini tayyorlayman.)

---

# 7) Xavfsizlik, deployment va ehtiyotkorlik

* **Unsigned driver → cheklovlar.** Korporativda driverlarni imzolash (EV cert) talab qilinadi.
* **Stabilnost:** kernel filter noto‘g‘ri yozilsa tizim barqarorligiga ta’sir ko‘rsatadi — unit testing va VMda keng sinov zarur.
* **Alternativ (kamroq invaziv):** Group Policy / Device Installation Restrictions yoki DeviceGuard kabi endpoint-level siyosatlarni qo‘llash (agar siz faqat mass storage bloklashni istasangiz, registry/Group Policy orqali ham bajarish mumkin).

---

Xulosa: agar siz **yuqori tezlikda aniqlash va ishonchli bloklash** (korporativ xavfsizlik uchun) istasangiz — **KMDF kernel-mode upper filter driver** (hub yoki host controller ustida) eng to‘g‘ri yechim. Agar faqat monitoring va jurnal kerak bo‘lsa, user-mode WMI / SetupAPI tezroq va yengil variant.

Xohlaysizmi:

* Men hozir **KMDF upper filter driver** uchun **oddiy skeleton (template) kod** va INF faylini tayyorlab beray (shu bilan birga qanday test qilish — VM/driver signing), yoki
* Avvalo sizga yuqoridagi Microsoft rasmiy hujjatlarining toʻliq linklarini joʻnatay?

Qaysi varianti darhol yuborishimni xohlaysiz?

[1]: https://learn.microsoft.com/en-us/windows-hardware/drivers/usbcon/usb-3-0-driver-stack-architecture?utm_source=chatgpt.com "USB Host-Side Drivers in Windows"
[2]: https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/registering-for-target-device-change-notification?utm_source=chatgpt.com "Registering for Target Device Change Notification"
[3]: https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/example-wdm-device-stack?utm_source=chatgpt.com "Example WDM Device Stack - Windows drivers"
[4]: https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/ntddk/nf-ntddk-ioattachdevicetodevicestacksafe?utm_source=chatgpt.com "IoAttachDeviceToDeviceStackSafe function (ntddk.h)"
[5]: https://learn.microsoft.com/en-us/windows-hardware/drivers/wdf/sample-kmdf-drivers?utm_source=chatgpt.com "Sample KMDF Drivers - Windows"
[6]: https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-ioregisterplugplaynotification?utm_source=chatgpt.com "IoRegisterPlugPlayNotification function (wdm.h)"
[7]: https://learn.microsoft.com/en-us/windows-hardware/drivers/samples/universal-serial-bus--usb--driver-samples?utm_source=chatgpt.com "Universal Serial Bus (USB) Driver Samples"
[8]: https://github.com/microsoft/Windows-driver-samples?utm_source=chatgpt.com "microsoft/Windows-driver-samples"
