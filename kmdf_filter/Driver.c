/*
 * UsbFilterDriver.c
 * KMDF Upper Filter Driver — USB qurilmalarni kernel darajasida bloklash.
 *
 * Ishlash printsipi:
 *   1. Bu driver USB hub yoki USBSTOR class devicening "upper filter" sifatida
 *      device stack'iga qo'shiladi (INF fayl orqali).
 *   2. Har bir yangi qurilma ulanganda EvtDeviceAdd chaqiriladi.
 *   3. IRP_MN_START_DEVICE so'rovi ushlab olinadi — bu nuqtada qurilmani
 *      ruxsat etilganlar ro'yxati (whitelist) bilan solishtirib bloklash mumkin.
 *   4. Bloklash uchun IRP STATUS_ACCESS_DENIED bilan yakunlanadi —
 *      qurilma Windows tomonidan "ishga tushirilmaydi" (disabled holat).
 *
 * Qurilish:
 *   - Visual Studio + WDK (Windows Driver Kit) o'rnatilgan bo'lishi kerak
 *   - "Kernel Mode Driver (KMDF)" loyihasi sifatida yarating
 *   - Platformalar: x64 (Windows 10/11)
 *
 * DIQQAT:
 *   - Kernel driverlari imzolanishi kerak (EV Code Signing Certificate)
 *   - Test uchun "bcdedit /set testsigning on" buyrug'ini ishlating
 *   - Xato bo'lsa BSOD (ko'k ekran) chiqishi mumkin — VMda sinab ko'ring
 */

#include <ntddk.h>
#include <wdf.h>
#include <usbiodef.h>
#include <initguid.h>
#include <usbioctl.h>

/* ─── Whitelist: ruxsat etilgan seriya raqamlar ──────────────────────────── */
/*
 * Haqiqiy loyihada bu ro'yxat:
 *   - Registry'dan o'qiladi (HKLM\SOFTWARE\UsbFilter\Whitelist)
 *   - Yoki user-mode agent tomonidan shared memory orqali yangilanadi
 *   - Yoki himoyalangan fayldan o'qiladi
 * Hozircha statik misol sifatida ko'rsatilgan.
 */
static const WCHAR* g_AllowedSerials[] = {
    L"E8238FA6BF530001001B448B4A21D14E",   /* Misol serial 1 */
    L"7956101095918431346",                  /* Misol serial 2 */
    NULL                                     /* Ro'yxat oxiri */
};

/* ─── Qurilma context ────────────────────────────────────────────────────── */
typedef struct _DEVICE_CONTEXT {
    BOOLEAN IsBlocked;          /* Qurilma bloklanganmi */
    WCHAR   Serial[128];        /* Qurilma seriya raqami */
    WCHAR   DeviceType[32];     /* "USB_FLASH" | "EXTERNAL_HDD" | ... */
} DEVICE_CONTEXT, *PDEVICE_CONTEXT;

WDF_DECLARE_CONTEXT_TYPE_WITH_NAME(DEVICE_CONTEXT, GetDeviceContext)

/* ─── Forward deklaratsiyalar ────────────────────────────────────────────── */
DRIVER_INITIALIZE DriverEntry;
EVT_WDF_DRIVER_DEVICE_ADD EvtDeviceAdd;
EVT_WDF_IO_QUEUE_IO_INTERNAL_DEVICE_CONTROL EvtInternalDeviceControl;

/* ─── Yordamchi: Seriyani whitelist bilan solishtirish ───────────────────── */
static BOOLEAN IsSerialAllowed(const WCHAR* serial) {
    if (!serial || serial[0] == L'\0') {
        /* Seriya raqami yo'q — bloklash (xavfsizlik siyosati) */
        return FALSE;
    }
    for (int i = 0; g_AllowedSerials[i] != NULL; i++) {
        if (_wcsicmp(serial, g_AllowedSerials[i]) == 0) {
            return TRUE;
        }
    }
    return FALSE;
}

/* ─── Yordamchi: USB Storage descriptor dan serial o'qish ───────────────── */
static void ExtractSerialFromDeviceId(
    WDFDEVICE Device,
    PWCHAR    SerialOut,
    SIZE_T    SerialOutSize
) {
    WDFMEMORY   memory = NULL;
    NTSTATUS    status;
    PWCHAR      idBuf   = NULL;
    SIZE_T      bufSize = 0;

    SerialOut[0] = L'\0';

    /* DeviceID ni o'qish: "USBSTOR\DISK&VEN_...&PROD_...&REV_...\<SERIAL>&0" */
    status = WdfDeviceAllocAndQueryProperty(
        Device,
        DevicePropertyHardwareID,
        NonPagedPoolNx,
        WDF_NO_OBJECT_ATTRIBUTES,
        &memory
    );

    if (!NT_SUCCESS(status) || memory == NULL) {
        return;
    }

    idBuf   = (PWCHAR)WdfMemoryGetBuffer(memory, &bufSize);
    if (!idBuf) goto Cleanup;

    /*
     * HardwareID multi-string ko'rinishida keladi.
     * USBSTOR\DISK&VEN_VENDORCO&PROD_PRODUCTCODE&REV_2.00 kabi.
     * Serial raqam DeviceInstanceId'ning oxirgi qismida bo'ladi: "<SERIAL>&0"
     */
    WDFSTRING wdfStr = NULL;
    status = WdfDeviceAllocAndQueryProperty(
        Device,
        DevicePropertyDeviceDescription,
        NonPagedPoolNx,
        WDF_NO_OBJECT_ATTRIBUTES,
        &memory
    );

    /* DeviceInstanceId orqali serial olish (to'liq yo'l: USBSTOR\...\SERIAL&0) */
    /* Bu oddiy misol — haqiqiy loyihada IoGetDeviceProperty ishlatiladi */
    UNICODE_STRING instanceId;
    WCHAR          instanceBuf[512] = {0};
    instanceId.Buffer    = instanceBuf;
    instanceId.MaximumLength = sizeof(instanceBuf) - sizeof(WCHAR);
    instanceId.Length    = 0;

    /* Instance ID'ning oxirgi qismini ajratish */
    PWCHAR p = idBuf;
    PWCHAR lastBackslash = NULL;
    while (*p) {
        if (*p == L'\\') lastBackslash = p;
        p++;
    }

    if (lastBackslash) {
        PWCHAR serialStart = lastBackslash + 1;
        /* "&0" yoki "&1" qismini olib tashlash */
        PWCHAR amp = wcsrchr(serialStart, L'&');
        SIZE_T len = amp ? (SIZE_T)(amp - serialStart) : wcslen(serialStart);
        len = min(len, SerialOutSize / sizeof(WCHAR) - 1);
        wcsncpy_s(SerialOut, SerialOutSize / sizeof(WCHAR), serialStart, len);
        SerialOut[len] = L'\0';
    }

Cleanup:
    if (memory) WdfObjectDelete(memory);
}

/* ─── Qurilma turini aniqlash (PnP class va HardwareID asosida) ─────────── */
static void DetermineDeviceType(
    const WCHAR* hardwareId,
    PWCHAR       DeviceTypeOut,
    SIZE_T       DeviceTypeOutSize
) {
    if (wcsstr(hardwareId, L"USBSTOR\\DISK")) {
        /*
         * Disk qurilma — USB Flash, tashqi HDD yoki M.2 adapter.
         * Faqat kernel'da media type yo'q, shuning uchun umumiy nom.
         * User-mode agent WMI orqali aniqroq aniqlaydi.
         */
        wcscpy_s(DeviceTypeOut, DeviceTypeOutSize / sizeof(WCHAR), L"USB_STORAGE");
    } else if (wcsstr(hardwareId, L"WPD")) {
        wcscpy_s(DeviceTypeOut, DeviceTypeOutSize / sizeof(WCHAR), L"PHONE_MTP");
    } else if (wcsstr(hardwareId, L"USB\\Class_08")) {
        wcscpy_s(DeviceTypeOut, DeviceTypeOutSize / sizeof(WCHAR), L"USB_MASS_STORAGE");
    } else {
        wcscpy_s(DeviceTypeOut, DeviceTypeOutSize / sizeof(WCHAR), L"USB_OTHER");
    }
}

/* ─── PnP IRP handler: IRP_MN_START_DEVICE nuqtasida bloklash ───────────── */
NTSTATUS FilterPnpStartDevice(
    IN WDFDEVICE Device,
    IN PIRP       Irp
)
{
    PDEVICE_CONTEXT ctx = GetDeviceContext(Device);

    /* Seriya raqamini o'qish */
    ExtractSerialFromDeviceId(Device, ctx->Serial, sizeof(ctx->Serial));

    KdPrint(("UsbFilter: Yangi qurilma ulandi. Serial: %ws\n", ctx->Serial));

    /* Whitelist tekshirish */
    if (!IsSerialAllowed(ctx->Serial)) {
        ctx->IsBlocked = TRUE;
        KdPrint(("UsbFilter: BLOKLANDI — Serial ro'yxatda yo'q: %ws\n", ctx->Serial));

        /*
         * IRP'ni muvaffaqiyatsiz yakunlash — qurilma "disabled" bo'ladi.
         * STATUS_ACCESS_DENIED → Windows "Qurilma ishga tushmadi" xabar beradi.
         */
        Irp->IoStatus.Status      = STATUS_ACCESS_DENIED;
        Irp->IoStatus.Information = 0;
        IoCompleteRequest(Irp, IO_NO_INCREMENT);
        return STATUS_ACCESS_DENIED;
    }

    ctx->IsBlocked = FALSE;
    KdPrint(("UsbFilter: RUXSAT — Serial topildi: %ws\n", ctx->Serial));

    /* IRP'ni keyingi drayverga uzatish */
    IoSkipCurrentIrpStackLocation(Irp);
    return IoCallDriver(WdfDeviceWdmGetAttachedDevice(Device), Irp);
}

/* ─── KMDF IRP pre-process callback ─────────────────────────────────────── */
NTSTATUS EvtDeviceWdmIrpPreprocess(
    WDFDEVICE Device,
    PIRP       Irp
)
{
    PIO_STACK_LOCATION stack = IoGetCurrentIrpStackLocation(Irp);

    if (stack->MajorFunction == IRP_MJ_PNP &&
        stack->MinorFunction == IRP_MN_START_DEVICE)
    {
        return FilterPnpStartDevice(Device, Irp);
    }

    /* Boshqa IRP'lar o'zgarishsiz o'tadi */
    IoSkipCurrentIrpStackLocation(Irp);
    return IoCallDriver(WdfDeviceWdmGetAttachedDevice(Device), Irp);
}

/* ─── EvtDeviceAdd: yangi qurilma stack'iga qo'shilganda ────────────────── */
NTSTATUS EvtDeviceAdd(
    _In_    WDFDRIVER        Driver,
    _Inout_ PWDFDEVICE_INIT  DeviceInit
)
{
    NTSTATUS              status;
    WDFDEVICE             device;
    WDF_OBJECT_ATTRIBUTES attribs;

    UNREFERENCED_PARAMETER(Driver);

    /* Filter device sifatida belgilash */
    WdfFdoInitSetFilter(DeviceInit);

    /* Device context */
    WDF_OBJECT_ATTRIBUTES_INIT_CONTEXT_TYPE(&attribs, DEVICE_CONTEXT);

    /* WDM IRP pre-process: PnP IRP'larni ushlash */
    status = WdfDeviceInitAssignWdmIrpPreprocessCallback(
        DeviceInit,
        EvtDeviceWdmIrpPreprocess,
        IRP_MJ_PNP,
        NULL,
        0
    );
    if (!NT_SUCCESS(status)) {
        KdPrint(("UsbFilter: WdfDeviceInitAssignWdmIrpPreprocessCallback xato: 0x%X\n", status));
        return status;
    }

    /* WDFDEVICE yaratish */
    status = WdfDeviceCreate(&DeviceInit, &attribs, &device);
    if (!NT_SUCCESS(status)) {
        KdPrint(("UsbFilter: WdfDeviceCreate xato: 0x%X\n", status));
        return status;
    }

    /* Context'ni tozalash */
    PDEVICE_CONTEXT ctx = GetDeviceContext(device);
    RtlZeroMemory(ctx, sizeof(DEVICE_CONTEXT));

    KdPrint(("UsbFilter: Yangi filter device qo'shildi.\n"));
    return STATUS_SUCCESS;
}

/* ─── DriverEntry: driver yuklanishi ────────────────────────────────────── */
NTSTATUS DriverEntry(
    _In_ PDRIVER_OBJECT  DriverObject,
    _In_ PUNICODE_STRING RegistryPath
)
{
    NTSTATUS          status;
    WDF_DRIVER_CONFIG config;

    KdPrint(("UsbFilter: DriverEntry — USB filter driver yuklanmoqda.\n"));

    WDF_DRIVER_CONFIG_INIT(&config, EvtDeviceAdd);

    status = WdfDriverCreate(
        DriverObject,
        RegistryPath,
        WDF_NO_OBJECT_ATTRIBUTES,
        &config,
        WDF_NO_HANDLE
    );

    if (!NT_SUCCESS(status)) {
        KdPrint(("UsbFilter: WdfDriverCreate xato: 0x%X\n", status));
        return status;
    }

    KdPrint(("UsbFilter: Driver muvaffaqiyatli yuklandi.\n"));
    return STATUS_SUCCESS;
}
